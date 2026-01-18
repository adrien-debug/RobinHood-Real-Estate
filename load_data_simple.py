#!/usr/bin/env python3
"""
Script simple pour charger les données dans Supabase via REST API
"""
import pandas as pd
import httpx
import json
from loguru import logger
from datetime import datetime

# Configuration Supabase
SUPABASE_URL = "https://tnnsfheflydiuhiduntn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRubnNmaGVmbHlkaXVoaWR1bnRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY1MTIxMjMsImV4cCI6MjA4MjA4ODEyM30.XZs44a7bNOrV2s6Aexne1sTP261L8wCprOSPO7XTuJo"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}


def test_connection():
    """Tester la connexion à Supabase"""
    logger.info("Test de connexion à Supabase...")
    
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{SUPABASE_URL}/rest/v1/dld_transactions?select=count",
                headers=HEADERS,
                timeout=10.0
            )
            
            if response.status_code == 200:
                logger.success(f"✓ Connexion OK (status: {response.status_code})")
                return True
            else:
                logger.error(f"✗ Erreur connexion: {response.status_code}")
                logger.error(f"  Response: {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"✗ Erreur: {e}")
        return False


def count_existing_transactions():
    """Compter les transactions existantes"""
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{SUPABASE_URL}/rest/v1/dld_transactions?select=transaction_id",
                headers={**HEADERS, "Prefer": "count=exact"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                # Le count est dans le header Content-Range
                content_range = response.headers.get('content-range', '')
                if '/' in content_range:
                    count = int(content_range.split('/')[-1])
                    logger.info(f"✓ {count} transactions déjà en base")
                    return count
                else:
                    return len(response.json())
            else:
                logger.warning(f"⚠ Impossible de compter: {response.status_code}")
                return 0
                
    except Exception as e:
        logger.error(f"✗ Erreur comptage: {e}")
        return 0


def load_transactions():
    """Charger les transactions depuis CSV"""
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║  CHARGEMENT TRANSACTIONS                                ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    
    # Charger le CSV
    df = pd.read_csv('data/transactions_12months.csv')
    logger.info(f"✓ {len(df)} transactions chargées depuis CSV")
    
    # Convertir en liste de dicts
    records = df.to_dict('records')
    
    # Insérer par batch de 50 (Supabase limite)
    batch_size = 50
    total_inserted = 0
    total_errors = 0
    
    with httpx.Client(timeout=30.0) as client:
        for i in range(0, len(records), batch_size):
            batch = records[i:i+batch_size]
            
            try:
                # Préparer les données
                supabase_batch = []
                for record in batch:
                    supabase_batch.append({
                        'transaction_id': record['transaction_id'],
                        'transaction_date': record['transaction_date'],
                        'transaction_type': record['transaction_type'],
                        'community': record['community'],
                        'project': record.get('project'),
                        'building': record.get('building'),
                        'property_type': record['property_type'],
                        'rooms_bucket': record.get('rooms_bucket'),
                        'area_sqft': float(record['area_sqft']) if pd.notna(record.get('area_sqft')) else None,
                        'price_aed': float(record['price_aed']),
                        'price_per_sqft': float(record['price_per_sqft']) if pd.notna(record.get('price_per_sqft')) else None,
                        'is_offplan': bool(record['is_offplan'])
                    })
                
                # POST avec upsert
                response = client.post(
                    f"{SUPABASE_URL}/rest/v1/dld_transactions",
                    headers={**HEADERS, "Prefer": "resolution=merge-duplicates"},
                    json=supabase_batch
                )
                
                if response.status_code in [200, 201, 204]:
                    total_inserted += len(batch)
                    logger.info(f"  ✓ Batch {i//batch_size + 1}/{(len(records)-1)//batch_size + 1}: {len(batch)} transactions")
                else:
                    total_errors += len(batch)
                    logger.error(f"  ✗ Batch {i//batch_size + 1}: {response.status_code}")
                    logger.error(f"    {response.text[:200]}")
                
            except Exception as e:
                total_errors += len(batch)
                logger.error(f"  ✗ Erreur batch {i//batch_size + 1}: {e}")
    
    logger.success(f"✓ {total_inserted} transactions insérées")
    if total_errors > 0:
        logger.warning(f"⚠ {total_errors} erreurs")
    
    return total_inserted


def get_sample_data():
    """Récupérer quelques exemples"""
    logger.info("\n📊 EXEMPLES DE DONNÉES")
    
    try:
        with httpx.Client() as client:
            response = client.get(
                f"{SUPABASE_URL}/rest/v1/dld_transactions?select=*&limit=5&order=transaction_date.desc",
                headers=HEADERS,
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                for tx in data:
                    logger.info(f"  {tx.get('transaction_date')} | {tx.get('community')} | {tx.get('property_type')} | {tx.get('price_aed'):,.0f} AED")
            else:
                logger.warning(f"⚠ Impossible de récupérer les exemples: {response.status_code}")
                
    except Exception as e:
        logger.error(f"✗ Erreur: {e}")


def main():
    """Fonction principale"""
    start_time = datetime.now()
    
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║                                                          ║")
    logger.info("║     CHARGEMENT DES DONNÉES DANS SUPABASE                ║")
    logger.info("║                                                          ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    logger.info("")
    
    # 1. Test connexion
    if not test_connection():
        logger.error("✗ Impossible de se connecter à Supabase")
        logger.info("\nVérifier:")
        logger.info("1. La table 'dld_transactions' existe")
        logger.info("2. Les permissions sont correctes")
        logger.info("3. L'URL et la clé API sont valides")
        return
    
    logger.info("")
    
    # 2. Compter existant
    existing = count_existing_transactions()
    logger.info("")
    
    # 3. Charger les données
    loaded = load_transactions()
    logger.info("")
    
    # 4. Vérifier après chargement
    final_count = count_existing_transactions()
    logger.info("")
    
    # 5. Exemples
    get_sample_data()
    logger.info("")
    
    # Résumé
    elapsed = datetime.now() - start_time
    
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║                                                          ║")
    logger.info("║                  RÉSUMÉ FINAL                            ║")
    logger.info("║                                                          ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    logger.info("")
    logger.info(f"Avant:              {existing:,} transactions")
    logger.info(f"Chargées:           {loaded:,} transactions")
    logger.info(f"Après:              {final_count:,} transactions")
    logger.info(f"Nouvelles:          {final_count - existing:,} transactions")
    logger.info(f"Temps total:        {elapsed}")
    logger.info("")
    
    if final_count > 0:
        logger.success("✓ DONNÉES CHARGÉES AVEC SUCCÈS")
        logger.info("")
        logger.info("Accès:")
        logger.info(f"  Dashboard Supabase: https://supabase.com/dashboard/project/tnnsfheflydiuhiduntn")
        logger.info(f"  Dashboard Next.js:  http://localhost:3000")
    else:
        logger.warning("⚠ AUCUNE DONNÉE EN BASE")


if __name__ == "__main__":
    main()
