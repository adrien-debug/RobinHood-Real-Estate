"""
Connexion et gestion de la base de données PostgreSQL
Compatible avec psycopg3 (psycopg) pour Streamlit Cloud
"""
from typing import Optional, Any, Dict, List
from contextlib import contextmanager
from urllib.parse import urlparse
import psycopg
from psycopg.rows import dict_row
from loguru import logger
from core.config import settings


def t(table_name: str) -> str:
    """Get table name with prefix (for Supabase compatibility)"""
    return f"{settings.table_prefix}{table_name}"


class Database:
    """Gestionnaire de connexion PostgreSQL"""
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or settings.database_url
        self._connection = None
    
    def _validate_connection_string(self):
        """Valider la chaîne de connexion pour erreurs courantes (sans secrets)."""
        if not self.connection_string:
            return

        if "[" in self.connection_string or "]" in self.connection_string:
            error_msg = (
                "❌ DATABASE_URL invalide : retirez les crochets [ ] autour du mot de passe.\n\n"
                "Exemple :\n"
                'DATABASE_URL="postgresql://postgres.<PROJECT_REF>:<PASSWORD>@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"'
            )
            logger.error("DATABASE_URL contient des crochets [ ]")
            raise ConnectionError(error_msg)

        parsed = urlparse(self.connection_string)
        host = parsed.hostname or ""
        user = parsed.username or ""
        local_hosts = {"localhost", "127.0.0.1", "::1"}

        if host.endswith(".pooler.supabase.com"):
            if user == "postgres" or not user.startswith("postgres."):
                error_msg = (
                    "❌ DATABASE_URL Supabase invalide (Pooler).\n\n"
                    "Le user doit être au format : postgres.<PROJECT_REF>\n"
                    "Exemple :\n"
                    'DATABASE_URL="postgresql://postgres.<PROJECT_REF>:<PASSWORD>@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"'
                )
                logger.error("DATABASE_URL Supabase Pooler sans project ref dans le user")
                raise ConnectionError(error_msg)

        if host.startswith("db.") and host.endswith(".supabase.co"):
            if user and user != "postgres" and not user.startswith("postgres."):
                logger.warning(
                    "DATABASE_URL Supabase (db.*) avec user inattendu. "
                    "Attendu: postgres ou postgres.<PROJECT_REF>."
                )

        if host in local_hosts and settings.table_prefix:
            logger.warning(
                "DATABASE_URL local détecté avec TABLE_PREFIX non vide. "
                "Pour une DB locale, TABLE_PREFIX devrait être vide."
            )

    def connect(self):
        """Établir la connexion"""
        if self._connection is None or self._connection.closed:
            try:
                # Vérifier que DATABASE_URL est configuré
                if not self.connection_string or self.connection_string == "postgresql://user:password@localhost:5432/dubai_real_estate":
                    error_msg = (
                        "❌ DATABASE_URL non configuré.\n\n"
                        "Sur Streamlit Cloud :\n"
                        "1. Cliquez sur 'Manage app' (en bas à droite)\n"
                        "2. Allez dans Settings > Secrets\n"
                        "3. Ajoutez : DATABASE_URL = \"postgresql://...\"\n"
                        "4. Cliquez sur 'Reboot app'\n\n"
                        "Voir STREAMLIT_SECRETS_SETUP.md pour plus de détails."
                    )
                    logger.error(error_msg)
                    raise ConnectionError(error_msg)
                
                self._validate_connection_string()
                self._connection = psycopg.connect(self.connection_string)
                # Configure search_path based on host type
                parsed = urlparse(self.connection_string)
                host = parsed.hostname or ""
                local_hosts = {"localhost", "127.0.0.1", "::1"}
                if host in local_hosts:
                    try:
                        with self._connection.cursor() as cur:
                            cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'robin'")
                            if cur.fetchone():
                                cur.execute("SET search_path TO robin, public")
                                logger.info("Search path défini sur robin, public (DB locale)")
                            else:
                                cur.execute("SET search_path TO public")
                                logger.info("Search path défini sur public (DB locale)")
                        self._connection.commit()
                    except Exception as e:
                        logger.warning(f"Search path local: {e}")
                        try:
                            self._connection.rollback()
                        except Exception:
                            pass
                else:
                    # Try to set search_path to robin schema (Supabase), fallback to public only
                    try:
                        with self._connection.cursor() as cur:
                            # Check if robin schema exists
                            cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'robin'")
                            if cur.fetchone():
                                cur.execute("SET search_path TO robin, public")
                                logger.info("Search path défini sur robin, public")
                            else:
                                cur.execute("SET search_path TO public")
                                logger.info("Schéma robin non trouvé, utilisation de public")
                        self._connection.commit()
                    except Exception as e:
                        logger.warning(f"Vérification schéma: {e}")
                        try:
                            self._connection.rollback()
                        except Exception:
                            pass
                logger.info("Connexion PostgreSQL établie")
            except psycopg.OperationalError as e:
                error_msg = (
                    f"❌ Impossible de se connecter à la base de données.\n\n"
                    f"Erreur : {str(e)}\n\n"
                    f"Vérifiez :\n"
                    f"1. DATABASE_URL est bien configuré dans les secrets Streamlit\n"
                    f"2. Le mot de passe est correct (pas d'espaces)\n"
                    f"3. La base Supabase est accessible\n\n"
                    f"Si le mot de passe contient /, =, @, etc., encodez-le en URL :\n"
                    f"  / devient %2F\n"
                    f"  = devient %3D\n"
                    f"  @ devient %40"
                )
                logger.error(error_msg)
                raise ConnectionError(error_msg) from e
            except Exception as e:
                logger.error(f"Erreur connexion DB : {e}")
                raise
        return self._connection
    
    def close(self):
        """Fermer la connexion"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            logger.info("Connexion PostgreSQL fermée")
    
    @contextmanager
    def get_cursor(self, dict_cursor: bool = True):
        """Context manager pour cursor"""
        conn = self.connect()
        row_factory = dict_row if dict_cursor else None
        cursor = conn.cursor(row_factory=row_factory)
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Erreur transaction DB : {e}")
            raise
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Exécuter une requête SELECT"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_insert(self, query: str, params: Optional[tuple] = None) -> Optional[Any]:
        """Exécuter un INSERT et retourner l'ID"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            try:
                return cursor.fetchone()
            except psycopg.ProgrammingError:
                # No results to fetch (e.g., after INSERT without RETURNING)
                return None
    
    def execute_batch_insert(self, table: str, columns: List[str], values: List[tuple]):
        """Insert batch optimisé"""
        if not values:
            return
        
        cols = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))
        query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
        
        with self.get_cursor(dict_cursor=False) as cursor:
            cursor.executemany(query, values)
            logger.info(f"Batch insert : {len(values)} lignes dans {table}")
    
    def execute_procedure(self, procedure_name: str, params: Optional[tuple] = None):
        """Exécuter une procédure stockée"""
        with self.get_cursor(dict_cursor=False) as cursor:
            if params:
                cursor.execute(f"CALL {procedure_name}(%s)", params)
            else:
                cursor.execute(f"CALL {procedure_name}()")
            logger.info(f"Procédure {procedure_name} exécutée")
    
    def init_schema(self):
        """Initialiser le schéma (exécuter schema.sql)"""
        import os
        schema_path = os.path.join(os.path.dirname(__file__), "..", "sql", "schema.sql")
        
        if not os.path.exists(schema_path):
            logger.warning(f"schema.sql introuvable : {schema_path}")
            return
        
        with open(schema_path, "r") as f:
            schema_sql = f.read()
        
        with self.get_cursor(dict_cursor=False) as cursor:
            cursor.execute(schema_sql)
            logger.info("Schéma initialisé")
    
    def load_sql_file(self, filepath: str):
        """Charger et exécuter un fichier SQL"""
        with open(filepath, "r") as f:
            sql = f.read()
        
        with self.get_cursor(dict_cursor=False) as cursor:
            cursor.execute(sql)
            logger.info(f"Fichier SQL chargé : {filepath}")


# Instance globale
db = Database()


def get_db_connection():
    """
    Obtenir une connexion à la base de données
    Compatible avec les anciens scripts
    """
    return db.connect()
