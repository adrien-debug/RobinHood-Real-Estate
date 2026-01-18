#!/usr/bin/env python3
"""
Script pour charger TOUTES les données dans Supabase
Utilise les données CSV + connexion Supabase Next.js
"""
import pandas as pd
import os
from datetime import datetime
from loguru import logger
from supabase import create_client, Client

# Configuration Supabase (depuis next-app/.env.local)
SUPABASE_URL = "https://tnnsfheflydiuhiduntn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRubnNmaGVmbHlkaXVoaWR1bnRuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY1MTIxMjMsImV4cCI6MjA4MjA4ODEyM30.XZs44a7bNOrV2s6Aexne1sTP261L8wCprOSPO7XTuJo"


def init_supabase() -> Client:
    """Initialiser le client Supabase"""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.success("✓ Client Supabase initialisé")
        return supabase
    except Exception as e:
        logger.error(f"✗ Erreur initialisation Supabase: {e}")
        raise


def create_tables(supabase: Client):
    """Créer les tables si elles n'existent pas"""
    logger.info("Création des tables...")
    
    # Note: Avec Supabase client Python, on ne peut pas créer les tables directement
    # Il faut les créer via l'interface Supabase ou via SQL
    logger.info("⚠ Les tables doivent être créées via l'interface Supabase")
    logger.info("  Tables nécessaires:")
    logger.info("  - dld_transactions")
    logger.info("  - bayut_listings")
    logger.info("  - dld_rental_index")
    logger.info("  - market_baselines")
    logger.info("  - market_regimes")
    logger.info("  - kpis")
    logger.info("  - opportunities")


def load_transactions(supabase: Client):
    """Charger les transactions depuis CSV"""
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║  CHARGEMENT TRANSACTIONS                                ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    
    csv_file = "data/transactions_12months.csv"
    
    if not os.path.exists(csv_file):
        logger.warning(f"⚠ Fichier {csv_file} introuvable")
        return 0
    
    # Charger le CSV
    df = pd.read_csv(csv_file)
    logger.info(f"✓ {len(df)} transactions chargées depuis CSV")
    
    # Convertir en liste de dicts
    records = df.to_dict('records')
    
    # Insérer par batch de 100
    batch_size = 100
    total_inserted = 0
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        
        try:
            # Préparer les données pour Supabase
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
            
            # Insert avec upsert
            result = supabase.table('dld_transactions').upsert(
                supabase_batch,
                on_conflict='transaction_id'
            ).execute()
            
            total_inserted += len(batch)
            logger.info(f"  ✓ Batch {i//batch_size + 1}: {len(batch)} transactions insérées")
            
        except Exception as e:
            logger.error(f"  ✗ Erreur batch {i//batch_size + 1}: {e}")
    
    logger.success(f"✓ TOTAL: {total_inserted} transactions chargées")
    return total_inserted


def verify_data(supabase: Client):
    """Vérifier les données chargées"""
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║  VÉRIFICATION DES DONNÉES                               ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    
    try:
        # Compter les transactions
        result = supabase.table('dld_transactions').select('transaction_id', count='exact').execute()
        count = result.count if hasattr(result, 'count') else len(result.data)
        
        logger.success(f"✓ {count} transactions en base")
        
        # Récupérer quelques exemples
        result = supabase.table('dld_transactions').select('*').limit(5).execute()
        
        if result.data:
            logger.info("\nExemples de transactions:")
            for tx in result.data[:3]:
                logger.info(f"  - {tx.get('community')} | {tx.get('property_type')} | {tx.get('price_aed'):,.0f} AED")
        
        return count
        
    except Exception as e:
        logger.error(f"✗ Erreur vérification: {e}")
        return 0


def compute_statistics(supabase: Client):
    """Calculer des statistiques de base"""
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║  CALCUL DES STATISTIQUES                                ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    
    try:
        # Récupérer toutes les transactions
        result = supabase.table('dld_transactions').select('*').execute()
        
        if not result.data:
            logger.warning("⚠ Aucune donnée à analyser")
            return
        
        df = pd.DataFrame(result.data)
        
        logger.info("\n📊 STATISTIQUES GLOBALES")
        logger.info(f"  Total transactions: {len(df):,}")
        logger.info(f"  Prix moyen: {df['price_aed'].mean():,.0f} AED")
        logger.info(f"  Prix médian: {df['price_aed'].median():,.0f} AED")
        logger.info(f"  Superficie moyenne: {df['area_sqft'].mean():,.0f} sqft")
        
        logger.info("\n📊 PAR TYPE DE PROPRIÉTÉ")
        type_counts = df['property_type'].value_counts()
        for prop_type, count in type_counts.head(5).items():
            logger.info(f"  {prop_type}: {count:,}")
        
        logger.info("\n📊 TOP 5 COMMUNAUTÉS")
        community_counts = df['community'].value_counts()
        for community, count in community_counts.head(5).items():
            logger.info(f"  {community}: {count:,}")
        
        logger.info("\n📊 PAR PÉRIODE")
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df['month'] = df['transaction_date'].dt.to_period('M')
        monthly = df.groupby('month').size()
        logger.info(f"  Transactions/mois (moy): {monthly.mean():.0f}")
        logger.info(f"  Mois le plus actif: {monthly.idxmax()} ({monthly.max()} tx)")
        
    except Exception as e:
        logger.error(f"✗ Erreur calcul statistiques: {e}")


def main():
    """Fonction principale"""
    start_time = datetime.now()
    
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║                                                          ║")
    logger.info("║     CHARGEMENT COMPLET DES DONNÉES DANS SUPABASE        ║")
    logger.info("║                                                          ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    logger.info("")
    
    # 1. Initialiser Supabase
    try:
        supabase = init_supabase()
    except Exception as e:
        logger.error("✗ Impossible d'initialiser Supabase")
        return
    
    logger.info("")
    
    # 2. Créer les tables (info seulement)
    create_tables(supabase)
    logger.info("")
    
    # 3. Charger les transactions
    total_loaded = load_transactions(supabase)
    logger.info("")
    
    # 4. Vérifier les données
    total_in_db = verify_data(supabase)
    logger.info("")
    
    # 5. Calculer les statistiques
    compute_statistics(supabase)
    logger.info("")
    
    # Résumé
    elapsed = datetime.now() - start_time
    
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║                                                          ║")
    logger.info("║                  RÉSUMÉ FINAL                            ║")
    logger.info("║                                                          ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    logger.info("")
    logger.info(f"Transactions chargées:  {total_loaded:,}")
    logger.info(f"Transactions en base:   {total_in_db:,}")
    logger.info(f"Temps total:            {elapsed}")
    logger.info("")
    
    if total_in_db > 0:
        logger.success("✓ DONNÉES CHARGÉES AVEC SUCCÈS")
        logger.info("")
        logger.info("Prochaines étapes:")
        logger.info("1. Vérifier les données dans Supabase: https://supabase.com/dashboard")
        logger.info("2. Consulter le dashboard Next.js: http://localhost:3000")
        logger.info("3. Calculer les KPIs et scores")
    else:
        logger.warning("⚠ AUCUNE DONNÉE CHARGÉE")
        logger.info("")
        logger.info("Vérifier:")
        logger.info("1. La table 'dld_transactions' existe dans Supabase")
        logger.info("2. Les permissions sont correctes")
        logger.info("3. Le fichier data/transactions_12months.csv existe")


if __name__ == "__main__":
    main()
