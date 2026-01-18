"""
Script de configuration automatique du fichier .env

Configure automatiquement toutes les cles API dans .env

Usage:
    python configure_env.py
"""
from pathlib import Path


def configure_env():
    """Configuration interactive du fichier .env"""
    
    print("=" * 60)
    print("CONFIGURATION AUTOMATIQUE DES APIs")
    print("=" * 60)
    print()
    
    env_path = Path(".env")
    
    # Lire le contenu actuel
    if env_path.exists():
        with open(env_path, 'r') as f:
            env_content = f.read()
    else:
        # Copier depuis env.example
        env_example = Path("env.example")
        if env_example.exists():
            with open(env_example, 'r') as f:
                env_content = f.read()
        else:
            env_content = ""
    
    print("Je vais te demander les cles API une par une.")
    print("Si tu n'as pas encore la cle, appuie juste sur ENTREE.")
    print()
    
    # Smart Indexes / Bayut
    print("1. BAYUT API")
    print("   Source : Smart Indexes (recommande) ou Bayut direct")
    print()
    bayut_key = input("   Entre ta cle Bayut (ou ENTREE pour skip) : ").strip()
    
    if bayut_key:
        # Mettre a jour dans env_content
        if "BAYUT_API_KEY=" in env_content:
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("BAYUT_API_KEY="):
                    lines[i] = f"BAYUT_API_KEY={bayut_key}"
            env_content = '\n'.join(lines)
        else:
            env_content += f"\nBAYUT_API_KEY={bayut_key}"
        
        print("   ✓ Cle Bayut configuree")
    else:
        print("   ⊘ Bayut skip (mode MOCK)")
    
    print()
    
    # Makani
    print("2. MAKANI API")
    print("   Source : Smart Indexes (recommande) ou GeoHub")
    print()
    makani_key = input("   Entre ta cle Makani (ou ENTREE pour skip) : ").strip()
    
    if makani_key:
        if "MAKANI_API_KEY=" in env_content:
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("MAKANI_API_KEY="):
                    lines[i] = f"MAKANI_API_KEY={makani_key}"
            env_content = '\n'.join(lines)
        else:
            env_content += f"\nMAKANI_API_KEY={makani_key}"
        
        print("   ✓ Cle Makani configuree")
    else:
        print("   ⊘ Makani skip (mode MOCK)")
    
    print()
    
    # DDA
    print("3. DDA API")
    print("   Source : Dubai Municipality")
    print()
    dda_key = input("   Entre ta cle DDA (ou ENTREE pour skip) : ").strip()
    
    if dda_key:
        if "DDA_API_KEY=" in env_content:
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("DDA_API_KEY="):
                    lines[i] = f"DDA_API_KEY={dda_key}"
            env_content = '\n'.join(lines)
        else:
            env_content += f"\nDDA_API_KEY={dda_key}"
        
        print("   ✓ Cle DDA configuree")
    else:
        print("   ⊘ DDA skip (mode MOCK)")
    
    print()
    
    # Dubai Pulse (DLD)
    print("4. DUBAI PULSE (DLD)")
    print("   Source : Dubai Pulse")
    print()
    dld_key = input("   Entre ton CLIENT_ID DLD (ou ENTREE pour skip) : ").strip()
    dld_secret = input("   Entre ton CLIENT_SECRET DLD (ou ENTREE pour skip) : ").strip()
    
    if dld_key and dld_secret:
        if "DLD_API_KEY=" in env_content:
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("DLD_API_KEY="):
                    lines[i] = f"DLD_API_KEY={dld_key}"
                elif line.startswith("DLD_API_SECRET="):
                    lines[i] = f"DLD_API_SECRET={dld_secret}"
            env_content = '\n'.join(lines)
        else:
            env_content += f"\nDLD_API_KEY={dld_key}"
            env_content += f"\nDLD_API_SECRET={dld_secret}"
        
        print("   ✓ Cles Dubai Pulse configurees")
    else:
        print("   ⊘ Dubai Pulse skip (mode MOCK)")
    
    print()
    
    # Sauvegarder .env
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("=" * 60)
    print("CONFIGURATION TERMINEE")
    print("=" * 60)
    print()
    print(f"Fichier .env sauvegarde : {env_path.absolute()}")
    print()
    print("Prochaines etapes :")
    print()
    print("1. Teste les APIs :")
    print("   python test_all_apis.py")
    print()
    print("2. Lance l'application :")
    print("   streamlit run app.py")
    print()
    print("3. Si certaines APIs sont en mode MOCK :")
    print("   - Obtiens les cles manquantes")
    print("   - Relance ce script pour les ajouter")
    print()


if __name__ == "__main__":
    configure_env()
