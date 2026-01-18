#!/usr/bin/env python3
"""
Script pour récupérer TOUTES les données historiques et les stocker en CSV
Permet de consolider les données même sans connexion DB
"""
from datetime import datetime, timedelta, date
from loguru import logger
from connectors.dld_transactions import DLDTransactionsConnector
from connectors.bayut_api import BayutAPIConnector
from connectors.dld_rental_index import DLDRentalIndexConnector
import pandas as pd
import time
import os


def fetch_all_transactions(months_back: int = 12):
    """
    Récupère toutes les transactions historiques
    """
    logger.info(f"╔══════════════════════════════════════════════════════════╗")
    logger.info(f"║  RÉCUPÉRATION TRANSACTIONS ({months_back} mois)                  ║")
    logger.info(f"╚══════════════════════════════════════════════════════════╝")
    
    connector = DLDTransactionsConnector()
    
    end_date = date.today()
    start_date = end_date - timedelta(days=months_back * 30)
    
    logger.info(f"Période: {start_date} → {end_date}")
    
    all_transactions = []
    current_date = start_date
    
    while current_date < end_date:
        chunk_end = min(current_date + timedelta(days=30), end_date)
        
        logger.info(f"Récupération: {current_date} → {chunk_end}")
        
        try:
            transactions = connector.fetch_transactions(
                start_date=current_date,
                end_date=chunk_end
            )
            
            if transactions:
                logger.info(f"  ✓ {len(transactions)} transactions")
                all_transactions.extend(transactions)
            
            time.sleep(2)  # Rate limiting
            
        except Exception as e:
            logger.error(f"  ✗ Erreur: {e}")
        
        current_date = chunk_end
    
    logger.success(f"✓ TOTAL: {len(all_transactions)} transactions récupérées")
    return all_transactions


def fetch_all_listings(days_back: int = 90):
    """
    Récupère toutes les annonces historiques
    """
    logger.info(f"╔══════════════════════════════════════════════════════════╗")
    logger.info(f"║  RÉCUPÉRATION ANNONCES ({days_back} jours)                       ║")
    logger.info(f"╚══════════════════════════════════════════════════════════╝")
    
    connector = BayutAPIConnector()
    
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
    
    all_listings = []
    
    for location in locations:
        logger.info(f"Récupération: {location}")
        
        try:
            page = 0
            while page < 20:  # Max 20 pages
                listings = connector.fetch_listings(
                    location=location,
                    days_back=days_back,
                    page=page
                )
                
                if not listings:
                    break
                
                logger.info(f"  Page {page}: {len(listings)} annonces")
                all_listings.extend(listings)
                
                page += 1
                time.sleep(1)
            
        except Exception as e:
            logger.error(f"  ✗ Erreur {location}: {e}")
    
    logger.success(f"✓ TOTAL: {len(all_listings)} annonces récupérées")
    return all_listings


def fetch_rental_index():
    """
    Récupère l'index locatif
    """
    logger.info(f"╔══════════════════════════════════════════════════════════╗")
    logger.info(f"║  RÉCUPÉRATION INDEX LOCATIF                             ║")
    logger.info(f"╚══════════════════════════════════════════════════════════╝")
    
    connector = DLDRentalIndexConnector()
    current_year = date.today().year
    
    try:
        rental_data = connector.fetch_rental_index(year=current_year, quarter=None)
        
        if rental_data:
            logger.success(f"✓ {len(rental_data)} entrées récupérées")
            return rental_data
        else:
            logger.warning("⚠ Aucune donnée")
            return []
            
    except Exception as e:
        logger.error(f"✗ Erreur: {e}")
        return []


def save_to_csv(data, filename, data_type="transactions"):
    """
    Sauvegarde les données en CSV
    """
    if not data:
        logger.warning(f"Aucune donnée à sauvegarder pour {filename}")
        return
    
    # Créer le dossier data/ si nécessaire
    os.makedirs("data", exist_ok=True)
    
    filepath = f"data/{filename}"
    
    # Convertir en DataFrame
    if data_type == "transactions":
        df = pd.DataFrame([{
            'transaction_id': t.transaction_id,
            'transaction_date': t.transaction_date,
            'transaction_type': t.transaction_type,
            'community': t.community,
            'project': t.project,
            'building': t.building,
            'property_type': t.property_type,
            'rooms_bucket': t.rooms_bucket,
            'area_sqft': float(t.area_sqft) if t.area_sqft else None,
            'price_aed': float(t.price_aed),
            'price_per_sqft': float(t.price_per_sqft) if t.price_per_sqft else None,
            'is_offplan': t.is_offplan
        } for t in data])
    
    elif data_type == "listings":
        df = pd.DataFrame([{
            'listing_id': l.listing_id,
            'location': l.location,
            'property_type': l.property_type,
            'rooms': l.rooms,
            'price_aed': float(l.price_aed),
            'area_sqft': float(l.area_sqft) if l.area_sqft else None,
            'price_per_sqft': float(l.price_per_sqft) if l.price_per_sqft else None,
            'days_on_market': l.days_on_market,
            'price_changes': l.price_changes,
            'is_new_listing': l.is_new_listing,
            'listing_date': l.listing_date,
            'last_updated': l.last_updated
        } for l in data])
    
    elif data_type == "rental":
        df = pd.DataFrame([{
            'community': r.community,
            'property_type': r.property_type,
            'rooms': r.rooms,
            'annual_rent_aed': float(r.annual_rent_aed),
            'quarter': r.quarter,
            'year': r.year
        } for r in data])
    
    # Sauvegarder
    df.to_csv(filepath, index=False)
    logger.success(f"✓ {len(df)} lignes sauvegardées dans {filepath}")
    
    # Afficher les stats
    logger.info(f"  Taille: {os.path.getsize(filepath) / 1024:.1f} KB")
    logger.info(f"  Colonnes: {len(df.columns)}")


def main():
    """
    Fonction principale
    """
    start_time = datetime.now()
    
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║                                                          ║")
    logger.info("║     RÉCUPÉRATION DONNÉES HISTORIQUES → CSV              ║")
    logger.info("║                                                          ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    logger.info("")
    
    # 1. Transactions (12 mois)
    transactions = fetch_all_transactions(months_back=12)
    logger.info("")
    save_to_csv(transactions, "transactions_12months.csv", "transactions")
    logger.info("")
    
    # 2. Annonces (90 jours)
    listings = fetch_all_listings(days_back=90)
    logger.info("")
    save_to_csv(listings, "listings_90days.csv", "listings")
    logger.info("")
    
    # 3. Index locatif
    rental = fetch_rental_index()
    logger.info("")
    save_to_csv(rental, "rental_index.csv", "rental")
    logger.info("")
    
    # Résumé
    elapsed = datetime.now() - start_time
    
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║                                                          ║")
    logger.info("║                  RÉSUMÉ FINAL                            ║")
    logger.info("║                                                          ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    logger.info("")
    logger.info(f"Transactions:  {len(transactions):,}")
    logger.info(f"Annonces:      {len(listings):,}")
    logger.info(f"Index locatif: {len(rental)}")
    logger.info("")
    logger.info(f"Temps total:   {elapsed}")
    logger.info("")
    logger.success("✓ DONNÉES SAUVEGARDÉES DANS ./data/")
    logger.info("")
    logger.info("Fichiers créés:")
    logger.info("  - data/transactions_12months.csv")
    logger.info("  - data/listings_90days.csv")
    logger.info("  - data/rental_index.csv")
    logger.info("")
    logger.info("Tu peux maintenant:")
    logger.info("  1. Analyser les CSV avec Excel/Python")
    logger.info("  2. Importer dans Supabase quand la connexion est réparée")
    logger.info("  3. Utiliser pour entraîner des modèles ML")


if __name__ == "__main__":
    main()
