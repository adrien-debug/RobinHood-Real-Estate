"""
Connexion et gestion de la base de données PostgreSQL
Compatible avec psycopg3 (psycopg) pour Streamlit Cloud
"""
from typing import Optional, Any, Dict, List
from contextlib import contextmanager
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
    
    def connect(self):
        """Établir la connexion"""
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg.connect(self.connection_string)
                # Set search_path for Supabase (robin schema first, then public)
                if 'supabase' in self.connection_string:
                    with self._connection.cursor() as cur:
                        cur.execute("SET search_path TO robin, public")
                    self._connection.commit()
                logger.info("Connexion PostgreSQL établie")
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
            except:
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
