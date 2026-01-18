"""
Script de configuration des APIs

Ce script aide à configurer les clés API dans le fichier .env
et vérifie que tout est correctement configuré.

Usage:
    python setup_apis.py
"""
import os
from pathlib import Path
import sys


class SimpleLogger:
    """Logger simple pour remplacer loguru"""
    
    @staticmethod
    def info(msg):
        print(f"[INFO] {msg}")
    
    @staticmethod
    def success(msg):
        print(f"[✓] {msg}")
    
    @staticmethod
    def warning(msg):
        print(f"[⚠] {msg}")
    
    @staticmethod
    def error(msg):
        print(f"[✗] {msg}")


logger = SimpleLogger()


def check_env_file():
    """Vérifier si le fichier .env existe"""
    env_path = Path(".env")
    env_example_path = Path("env.example")
    
    if not env_path.exists():
        logger.warning("⚠ Fichier .env non trouvé")
        
        if env_example_path.exists():
            logger.info("Création du fichier .env depuis env.example...")
            
            # Copier env.example vers .env
            with open(env_example_path, 'r') as f:
                content = f.read()
            
            with open(env_path, 'w') as f:
                f.write(content)
            
            logger.success("✓ Fichier .env créé")
            logger.info("Édite maintenant .env avec tes clés API")
            return False
        else:
            logger.error("✗ Fichier env.example non trouvé")
            return False
    
    return True


def read_env_file():
    """Lire le fichier .env et extraire les clés API"""
    env_vars = {}
    
    try:
        with open(".env", 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        logger.error(f"✗ Erreur lecture .env : {e}")
        return {}
    
    return env_vars


def check_api_keys():
    """Vérifier quelles clés API sont configurées"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("VÉRIFICATION DES CLÉS API")
    logger.info("=" * 60)
    
    env_vars = read_env_file()
    
    if not env_vars:
        logger.error("✗ Impossible de lire le fichier .env")
        return
    
    # Liste des clés API à vérifier
    api_keys = {
        "DLD_API_KEY": "Dubai Pulse (DLD Transactions)",
        "DLD_API_SECRET": "Dubai Pulse (DLD Secret)",
        "BAYUT_API_KEY": "Bayut API",
        "MAKANI_API_KEY": "Makani Geocoding",
        "DDA_API_KEY": "DDA Planning & Zoning",
    }
    
    configured = []
    missing = []
    
    for key, name in api_keys.items():
        value = env_vars.get(key, "")
        
        # Vérifier si la clé est configurée (pas vide et pas la valeur par défaut)
        is_configured = (
            value and 
            value != "" and 
            not value.startswith("your_") and
            not value.endswith("_here") and
            not value.endswith("_key")
        )
        
        if is_configured:
            # Masquer la clé (afficher seulement les 4 premiers caractères)
            masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "****"
            logger.success(f"✓ {name}: {masked}")
            configured.append(name)
        else:
            logger.warning(f"✗ {name}: Non configuré")
            missing.append((key, name))
    
    logger.info("")
    logger.info(f"Total : {len(configured)}/{len(api_keys)} APIs configurées")
    
    if missing:
        logger.info("")
        logger.info("=" * 60)
        logger.info("CLÉS MANQUANTES")
        logger.info("=" * 60)
        
        for key, name in missing:
            logger.info(f"• {name} ({key})")
        
        logger.info("")
        logger.info("Pour obtenir ces clés, consulte : API_LINKS.md")
    
    return configured, missing


def provide_instructions():
    """Fournir des instructions pour obtenir les clés API"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("COMMENT OBTENIR LES CLÉS API")
    logger.info("=" * 60)
    logger.info("")
    
    logger.info("1. Dubai Pulse (DLD)")
    logger.info("   URL : https://www.dubaipulse.gov.ae")
    logger.info("   Délai : 7-14 jours")
    logger.info("   Coût : Gratuit")
    logger.info("")
    
    logger.info("2. Bayut API")
    logger.info("   URL : https://www.bayut.com/partnerships")
    logger.info("   Email : partnerships@bayut.com")
    logger.info("   Délai : 2-4 semaines")
    logger.info("   Coût : Sur devis")
    logger.info("")
    
    logger.info("3. Makani Geocoding")
    logger.info("   URL : https://geohub.dubaipulse.gov.ae")
    logger.info("   Délai : 2-8 semaines")
    logger.info("   Coût : Gratuit")
    logger.info("")
    
    logger.info("4. DDA Planning")
    logger.info("   URL : https://www.dm.gov.ae/open-data")
    logger.info("   Email : dm@dm.gov.ae")
    logger.info("   Délai : 2-4 semaines")
    logger.info("   Coût : Gratuit")
    logger.info("")
    
    logger.info("=" * 60)
    logger.info("ALTERNATIVE RAPIDE : Smart Indexes")
    logger.info("=" * 60)
    logger.info("")
    logger.info("URL : https://smartindexes.com")
    logger.info("Coût : ~$199/mois (Plan Pro)")
    logger.info("Délai : Immédiat")
    logger.info("Inclut : Bayut + Makani + Price Indexes")
    logger.info("")
    logger.info("Recommandation : Utiliser Smart Indexes pendant que")
    logger.info("tu attends les accès officiels (gratuits mais lents)")
    logger.info("")


def update_env_file(key, value):
    """Mettre à jour une clé dans le fichier .env"""
    try:
        # Lire le contenu actuel
        with open(".env", 'r') as f:
            lines = f.readlines()
        
        # Chercher et remplacer la ligne
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                updated = True
                break
        
        # Si la clé n'existe pas, l'ajouter
        if not updated:
            lines.append(f"{key}={value}\n")
        
        # Écrire le nouveau contenu
        with open(".env", 'w') as f:
            f.writelines(lines)
        
        logger.success(f"✓ {key} mis à jour dans .env")
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur mise à jour .env : {e}")
        return False


def interactive_setup():
    """Configuration interactive des clés API"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("CONFIGURATION INTERACTIVE")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Veux-tu configurer les clés API maintenant ? (o/n)")
    
    try:
        response = input("> ").strip().lower()
        
        if response not in ['o', 'oui', 'y', 'yes']:
            logger.info("Configuration annulée")
            return
        
        # Liste des clés à configurer
        api_keys = {
            "DLD_API_KEY": "Dubai Pulse - Client ID",
            "DLD_API_SECRET": "Dubai Pulse - Client Secret",
            "BAYUT_API_KEY": "Bayut API Key",
            "MAKANI_API_KEY": "Makani API Key",
            "DDA_API_KEY": "DDA API Key",
        }
        
        for key, name in api_keys.items():
            logger.info("")
            logger.info(f"Configurer {name} ? (o/n/skip)")
            response = input("> ").strip().lower()
            
            if response in ['o', 'oui', 'y', 'yes']:
                logger.info(f"Entre la valeur pour {key}:")
                value = input("> ").strip()
                
                if value:
                    update_env_file(key, value)
                else:
                    logger.warning("Valeur vide, ignoré")
        
        logger.success("")
        logger.success("✓ Configuration terminée")
        logger.info("Relance ce script pour vérifier la configuration")
        
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Configuration interrompue")
    except Exception as e:
        logger.error(f"✗ Erreur : {e}")


def main():
    """Fonction principale"""
    logger.info("")
    logger.info("╔" + "═" * 58 + "╗")
    logger.info("║" + " " * 12 + "CONFIGURATION DES APIs" + " " * 23 + "║")
    logger.info("╚" + "═" * 58 + "╝")
    logger.info("")
    
    # Vérifier le fichier .env
    if not check_env_file():
        logger.info("")
        logger.info("Édite le fichier .env avec tes clés API, puis relance ce script")
        return
    
    # Vérifier les clés API
    configured, missing = check_api_keys()
    
    # Fournir des instructions
    if missing:
        provide_instructions()
        
        # Proposer configuration interactive
        logger.info("Veux-tu configurer les clés maintenant ? (o/n)")
        try:
            response = input("> ").strip().lower()
            if response in ['o', 'oui', 'y', 'yes']:
                interactive_setup()
        except:
            pass
    else:
        logger.success("")
        logger.success("╔" + "═" * 58 + "╗")
        logger.success("║" + " " * 10 + "✓ TOUTES LES APIs SONT CONFIGURÉES" + " " * 13 + "║")
        logger.success("╚" + "═" * 58 + "╝")
        logger.success("")
        logger.info("Prochaine étape : Tester les APIs")
        logger.info("  python test_all_apis.py")
    
    logger.info("")


if __name__ == "__main__":
    main()
