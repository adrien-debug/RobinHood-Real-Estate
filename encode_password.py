#!/usr/bin/env python3
"""
Script pour encoder le mot de passe Supabase et générer la config Streamlit
"""
import urllib.parse
import sys

def main():
    print("="*60)
    print("ENCODAGE MOT DE PASSE SUPABASE")
    print("="*60)
    print()
    
    # Demander le mot de passe
    print("Colle ton mot de passe Supabase ici (il ne sera pas affiché):")
    password = input().strip()
    
    if not password:
        print("❌ Erreur: mot de passe vide")
        sys.exit(1)
    
    # Encoder le mot de passe
    encoded_password = urllib.parse.quote(password, safe="")
    
    print()
    print("="*60)
    print("✅ MOT DE PASSE ENCODÉ")
    print("="*60)
    print()
    print(encoded_password)
    print()
    
    # Générer les configs
    print("="*60)
    print("CONFIG STREAMLIT SECRETS (POOLER)")
    print("="*60)
    print()
    print(f'DATABASE_URL = "postgresql://postgres.tnnsfheflydiuhiduntn:{encoded_password}@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"')
    print('TABLE_PREFIX = "dld_"')
    print('TIMEZONE = "Asia/Dubai"')
    print()
    
    print("="*60)
    print("CONFIG STREAMLIT SECRETS (DIRECT)")
    print("="*60)
    print()
    print(f'DATABASE_URL = "postgresql://postgres:{encoded_password}@db.tnnsfheflydiuhiduntn.supabase.co:5432/postgres"')
    print('TABLE_PREFIX = "dld_"')
    print('TIMEZONE = "Asia/Dubai"')
    print()
    
    print("="*60)
    print("PROCHAINES ÉTAPES")
    print("="*60)
    print()
    print("1. Copie UNE des configs ci-dessus (recommandé: POOLER)")
    print("2. Va sur: https://share.streamlit.io/")
    print("3. Trouve ton app → Manage app → Settings → Secrets")
    print("4. Colle la config complète")
    print("5. Clique Save → Reboot app")
    print("6. Attends 60 secondes")
    print()
    print("="*60)

if __name__ == "__main__":
    main()
