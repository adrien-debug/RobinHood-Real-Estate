#!/usr/bin/env python3
"""
Script pour ingérer TOUTES les données historiques possibles
Récupère le maximum de données via les APIs pour enrichir la base
"""
from datetime import datetime, timedelta, date
from loguru import logger
from core.db import db
from core.config import settings
from connectors.dld_transactions import DLDTransactionsConnector
from connectors.bayut_api import BayutAPIConnector
from connectors.dld_rental_index import DLDRentalIndexConnector
from pipelines.ingest_transactions import ingest_transactions
from pipelines.ingest_rental_index import ingest_rental_index as ingest_rental_pipeline
import time


def ingest_historical_transactions(months_back: int = 12):
    """
    Ingère les transactions historiques sur N mois
    
    Args:
        months_back: Nombre de mois à récupérer (défaut: 12)
    """
    logger.info(f"╔══════════════════════════════════════════════════════════╗")
    logger.info(f"║  INGESTION TRANSACTIONS HISTORIQUES ({months_back} mois)         ║")
    logger.info(f"╚══════════════════════════════════════════════════════════╝")
    
    end_date = date.today()
    start_date = end_date - timedelta(days=months_back * 30)
    
    logger.info(f"Période: {start_date} → {end_date}")
    
    # Récupérer les transactions par tranches de 30 jours
    current_date = start_date
    total_transactions = 0
    
    while current_date < end_date:
        chunk_end = min(current_date + timedelta(days=30), end_date)
        
        logger.info(f"Récupération: {current_date} → {chunk_end}")
        
        try:
            # Utiliser le pipeline d'ingestion
            inserted = ingest_transactions(
                start_date=current_date,
                end_date=chunk_end
            )
            
            if inserted > 0:
                logger.success(f"  ✓ {inserted} transactions insérées")
                total_transactions += inserted
            else:
                logger.warning(f"  ⚠ Aucune transaction pour cette période")
            
            # Pause pour éviter rate limiting
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"  ✗ Erreur: {e}")
        
        current_date = chunk_end
    
    logger.success(f"✓ TOTAL: {total_transactions} transactions historiques ingérées")
    return total_transactions


def ingest_historical_listings(days_back: int = 90):
    """
    Ingère les annonces historiques sur N jours
    
    Args:
        days_back: Nombre de jours à récupérer (défaut: 90)
    """
    logger.info(f"╔══════════════════════════════════════════════════════════╗")
    logger.info(f"║  INGESTION ANNONCES HISTORIQUES ({days_back} jours)            ║")
    logger.info(f"╚══════════════════════════════════════════════════════════╝")
    
    connector = BayutAPIConnector()
    
    # Principales zones de Dubai
    locations = [
        "dubai-marina",
        "downtown-dubai", 
        "business-bay",
        "jumeirah-beach-residence-jbr",
        "palm-jumeirah",
        "dubai-hills-estate",
        "arabian-ranches",
        "dubai-south",
        "meydan-city",
        "dubai-creek-harbour"
    ]
    
    total_listings = 0
    
    for location in locations:
        logger.info(f"Récupération annonces: {location}")
        
        try:
            # Récupérer toutes les annonces disponibles (pagination)
            page = 0
            location_total = 0
            
            while page < 20:  # Max 20 pages par location (500 annonces)
                listings = connector.fetch_listings(
                    location=location,
                    days_back=days_back,
                    page=page
                )
                
                if not listings:
                    break
                
                logger.info(f"  Page {page}: {len(listings)} annonces")
                
                # Insérer dans la base
                for listing in listings:
                    try:
                        db.execute_query("""
                            INSERT INTO bayut_listings (
                                listing_id, location, property_type, rooms,
                                price_aed, area_sqft, price_per_sqft,
                                days_on_market, price_changes, is_new_listing,
                                listing_date, last_updated
                            ) VALUES (
                                %(listing_id)s, %(location)s, %(property_type)s, %(rooms)s,
                                %(price_aed)s, %(area_sqft)s, %(price_per_sqft)s,
                                %(days_on_market)s, %(price_changes)s, %(is_new_listing)s,
                                %(listing_date)s, %(last_updated)s
                            )
                            ON CONFLICT (listing_id) DO UPDATE SET
                                price_aed = EXCLUDED.price_aed,
                                days_on_market = EXCLUDED.days_on_market,
                                price_changes = EXCLUDED.price_changes,
                                last_updated = EXCLUDED.last_updated
                        """, {
                            'listing_id': listing.listing_id,
                            'location': listing.location,
                            'property_type': listing.property_type,
                            'rooms': listing.rooms,
                            'price_aed': float(listing.price_aed),
                            'area_sqft': float(listing.area_sqft) if listing.area_sqft else None,
                            'price_per_sqft': float(listing.price_per_sqft) if listing.price_per_sqft else None,
                            'days_on_market': listing.days_on_market,
                            'price_changes': listing.price_changes,
                            'is_new_listing': listing.is_new_listing,
                            'listing_date': listing.listing_date,
                            'last_updated': listing.last_updated
                        })
                        location_total += 1
                    except Exception as e:
                        logger.debug(f"    Skip listing {listing.listing_id}: {e}")
                
                page += 1
                time.sleep(1)  # Rate limiting
            
            logger.success(f"  ✓ {location_total} annonces insérées pour {location}")
            total_listings += location_total
            
        except Exception as e:
            logger.error(f"  ✗ Erreur {location}: {e}")
    
    logger.success(f"✓ TOTAL: {total_listings} annonces historiques ingérées")
    return total_listings


def ingest_rental_index():
    """
    Ingère l'index locatif DLD
    """
    logger.info(f"╔══════════════════════════════════════════════════════════╗")
    logger.info(f"║  INGESTION INDEX LOCATIF DLD                            ║")
    logger.info(f"╚══════════════════════════════════════════════════════════╝")
    
    # Récupérer l'index pour l'année en cours
    current_year = date.today().year
    
    try:
        # Utiliser le pipeline d'ingestion
        inserted = ingest_rental_pipeline()
        
        if inserted > 0:
            logger.success(f"✓ {inserted} entrées insérées")
            return inserted
        else:
            logger.warning("⚠ Aucune donnée d'index locatif")
            return 0
            
    except Exception as e:
        logger.error(f"✗ Erreur: {e}")
        return 0


def compute_all_metrics():
    """
    Calcule tous les KPIs, baselines, régimes et scores
    """
    logger.info(f"╔══════════════════════════════════════════════════════════╗")
    logger.info(f"║  CALCUL DE TOUS LES MÉTRIQUES                           ║")
    logger.info(f"╚══════════════════════════════════════════════════════════╝")
    
    try:
        # Exécuter les pipelines de calcul
        logger.info("Calcul des features, baselines, régimes, KPIs et scores...")
        
        # Utiliser le job quotidien qui fait tout
        from jobs.daily_run import run_daily_pipeline
        run_daily_pipeline()
        
        logger.success("✓ TOUS LES MÉTRIQUES CALCULÉS")
        
    except Exception as e:
        logger.error(f"✗ Erreur lors du calcul des métriques: {e}")


def main():
    """
    Fonction principale - Ingestion complète
    """
    start_time = datetime.now()
    
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║                                                          ║")
    logger.info("║     INGESTION COMPLÈTE DES DONNÉES HISTORIQUES          ║")
    logger.info("║                                                          ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    logger.info("")
    
    # Vérifier la connexion DB
    try:
        db.execute_query("SELECT 1")
        logger.success("✓ Connexion base de données OK")
    except Exception as e:
        logger.error(f"✗ Erreur connexion DB: {e}")
        return
    
    logger.info("")
    
    # 1. Transactions historiques (12 mois)
    total_transactions = ingest_historical_transactions(months_back=12)
    logger.info("")
    
    # 2. Annonces historiques (90 jours)
    total_listings = ingest_historical_listings(days_back=90)
    logger.info("")
    
    # 3. Index locatif
    total_rental = ingest_rental_index()
    logger.info("")
    
    # 4. Calculer tous les métriques
    compute_all_metrics()
    logger.info("")
    
    # Résumé final
    elapsed = datetime.now() - start_time
    
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║                                                          ║")
    logger.info("║                  RÉSUMÉ FINAL                            ║")
    logger.info("║                                                          ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    logger.info("")
    logger.info(f"Transactions ingérées:  {total_transactions:,}")
    logger.info(f"Annonces ingérées:      {total_listings:,}")
    logger.info(f"Index locatif:          {total_rental}")
    logger.info("")
    logger.info(f"Temps total:            {elapsed}")
    logger.info("")
    logger.success("✓ INGESTION COMPLÈTE TERMINÉE")
    logger.info("")
    logger.info("Prochaines étapes:")
    logger.info("1. Vérifier les données dans Supabase")
    logger.info("2. Consulter le dashboard Next.js: http://localhost:3000")
    logger.info("3. Analyser les opportunités détectées")


if __name__ == "__main__":
    main()
