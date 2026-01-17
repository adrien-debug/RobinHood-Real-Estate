"""
Script de test de connexion à la base de données
Utilisé pour vérifier que DATABASE_URL est correctement configuré
"""
import sys
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

def test_connection():
    """Teste la connexion à la base de données"""
    
    print("\n" + "="*60)
    print("🔍 Test de Connexion à la Base de Données")
    print("="*60 + "\n")
    
    # 1. Vérifier la configuration
    print("1️⃣ Vérification de la configuration...")
    try:
        from core.config import settings
        
        if not settings.database_url:
            logger.error("❌ DATABASE_URL n'est pas défini")
            return False
        
        if settings.database_url == "postgresql://user:password@localhost:5432/dubai_real_estate":
            logger.error("❌ DATABASE_URL utilise la valeur par défaut (non configuré)")
            return False
        
        # Masquer le mot de passe dans l'affichage
        safe_url = settings.database_url
        if "@" in safe_url:
            parts = safe_url.split("@")
            if ":" in parts[0]:
                user_pass = parts[0].split(":")
                safe_url = f"{user_pass[0]}:****@{parts[1]}"
        
        logger.success(f"✅ DATABASE_URL configuré : {safe_url}")
        logger.info(f"   TABLE_PREFIX : {settings.table_prefix}")
        logger.info(f"   TIMEZONE : {settings.timezone}")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la lecture de la config : {e}")
        return False
    
    # 2. Tester la connexion
    print("\n2️⃣ Test de connexion à PostgreSQL...")
    try:
        from core.db import db
        
        conn = db.connect()
        logger.success("✅ Connexion établie avec succès")
        
        # Tester une requête simple
        print("\n3️⃣ Test d'une requête simple...")
        with db.get_cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            logger.success(f"✅ PostgreSQL version : {version['version'][:50]}...")
        
        # Vérifier le schéma robin
        print("\n4️⃣ Vérification du schéma 'robin'...")
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name = 'robin'
            """)
            schema = cursor.fetchone()
            
            if schema:
                logger.success("✅ Schéma 'robin' existe")
            else:
                logger.warning("⚠️ Schéma 'robin' n'existe pas encore")
                logger.info("   Utilisez la page Admin Data pour initialiser le schéma")
        
        # Vérifier les tables
        print("\n5️⃣ Vérification des tables...")
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'robin' 
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            
            if tables:
                logger.success(f"✅ {len(tables)} tables trouvées dans le schéma 'robin'")
                for table in tables[:5]:  # Afficher les 5 premières
                    logger.info(f"   - {table['table_name']}")
                if len(tables) > 5:
                    logger.info(f"   ... et {len(tables) - 5} autres")
            else:
                logger.warning("⚠️ Aucune table trouvée dans le schéma 'robin'")
                logger.info("   Utilisez la page Admin Data pour initialiser le schéma")
        
        db.close()
        
        print("\n" + "="*60)
        logger.success("✅ TOUS LES TESTS SONT PASSÉS")
        print("="*60 + "\n")
        
        return True
        
    except ConnectionError as e:
        logger.error(f"❌ Erreur de connexion : {e}")
        print("\n" + "="*60)
        print("❌ ÉCHEC DES TESTS")
        print("="*60 + "\n")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erreur inattendue : {e}")
        print("\n" + "="*60)
        print("❌ ÉCHEC DES TESTS")
        print("="*60 + "\n")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
