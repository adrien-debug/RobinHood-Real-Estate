"""
Pipeline : Calcul des features normalisées

Normalise les données de transactions et listings en features exploitables :
- Normalisation localisation (community/project/building)
- Normalisation prix en AED et prix/sqft
- Filtrage des outliers (< 500 AED/sqft ou > 10 000 AED/sqft)
- Différenciation listing (ask) vs transaction (real paid)
- Enrichissement avec données Makani (geo-features)
"""
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
import time
from loguru import logger

from core.db import db
from core.models import Feature, Transaction, Listing, QualityLog
from core.utils import (
    normalize_location_name, 
    normalize_rooms_bucket, 
    calculate_price_per_sqft,
    get_dubai_today
)
from connectors.makani_geocoding import MakaniGeocodingConnector


# Seuils de filtrage des outliers
MIN_PRICE_PER_SQFT = 500
MAX_PRICE_PER_SQFT = 10000


def compute_features(target_date: Optional[date] = None) -> Tuple[int, QualityLog]:
    """
    Pipeline principal de calcul des features
    
    1. Récupère transactions et listings récents
    2. Normalise les données
    3. Filtre les outliers
    4. Enrichit avec Makani
    5. Insère dans la table features
    6. Retourne le log de qualité
    
    Args:
        target_date: Date cible (défaut: aujourd'hui)
        
    Returns:
        Tuple (nombre de features insérées, log de qualité)
    """
    start_time = time.time()
    
    if not target_date:
        target_date = get_dubai_today()
    
    logger.info(f"Calcul des features pour {target_date}")
    
    # Initialiser les compteurs de qualité
    quality_stats = {
        "total": 0,
        "accepted": 0,
        "rejected": 0,
        "rejection_reasons": {
            "outliers": 0,
            "duplicates": 0,
            "missing_price": 0,
            "missing_area": 0,
            "invalid_data": 0
        },
        "field_completeness": {}
    }
    
    all_features = []
    
    # 1. Récupérer et traiter les transactions
    transactions = _fetch_recent_transactions(target_date)
    tx_features, tx_stats = _process_transactions(transactions)
    all_features.extend(tx_features)
    _merge_quality_stats(quality_stats, tx_stats, "transaction")
    
    # 2. Récupérer et traiter les listings
    listings = _fetch_recent_listings(target_date)
    listing_features, listing_stats = _process_listings(listings)
    all_features.extend(listing_features)
    _merge_quality_stats(quality_stats, listing_stats, "listing")
    
    # 3. Enrichir avec Makani (batch pour optimiser)
    all_features = _enrich_with_makani(all_features)
    
    # 4. Insérer dans la base
    inserted_count = _insert_features(all_features)
    
    # 5. Calculer les stats de complétude
    quality_stats["field_completeness"] = _calculate_field_completeness(all_features)
    
    # Créer le log de qualité
    execution_time_ms = int((time.time() - start_time) * 1000)
    
    quality_log = QualityLog(
        run_date=datetime.now(),
        source_type="features",
        pipeline_step="compute_features",
        records_total=quality_stats["total"],
        records_accepted=quality_stats["accepted"],
        records_rejected=quality_stats["rejected"],
        rejection_reasons=quality_stats["rejection_reasons"],
        field_completeness=quality_stats["field_completeness"],
        execution_time_ms=execution_time_ms,
        status="success" if quality_stats["rejected"] < quality_stats["total"] * 0.5 else "warning"
    )
    
    # Sauvegarder le log de qualité
    _save_quality_log(quality_log)
    
    logger.info(f"Features calculées : {inserted_count} insérées, {quality_stats['rejected']} rejetées en {execution_time_ms}ms")
    
    return inserted_count, quality_log


def _fetch_recent_transactions(target_date: date) -> List[Dict]:
    """Récupérer les transactions récentes (7 derniers jours)"""
    query = """
    SELECT 
        transaction_id,
        transaction_date,
        community,
        project,
        building,
        rooms_bucket,
        property_type,
        price_aed,
        price_per_sqft,
        area_sqft,
        is_offplan
    FROM transactions
    WHERE transaction_date >= %s - INTERVAL '7 days'
        AND transaction_date <= %s
    ORDER BY transaction_date DESC
    """
    try:
        results = db.execute_query(query, (target_date, target_date))
        logger.info(f"Transactions récupérées : {len(results)}")
        return results or []
    except Exception as e:
        logger.error(f"Erreur récupération transactions : {e}")
        return []


def _fetch_recent_listings(target_date: date) -> List[Dict]:
    """Récupérer les listings récents (actifs des 30 derniers jours)"""
    query = """
    SELECT 
        listing_id,
        listing_date,
        community,
        project,
        building,
        rooms_bucket,
        property_type,
        asking_price_aed,
        asking_price_per_sqft,
        area_sqft,
        days_on_market,
        price_changes
    FROM listings
    WHERE status = 'active'
        AND listing_date >= %s - INTERVAL '30 days'
    ORDER BY listing_date DESC
    """
    try:
        results = db.execute_query(query, (target_date,))
        logger.info(f"Listings récupérés : {len(results)}")
        return results or []
    except Exception as e:
        logger.error(f"Erreur récupération listings : {e}")
        return []


def _process_transactions(transactions: List[Dict]) -> Tuple[List[Feature], Dict]:
    """
    Traiter les transactions et les convertir en features
    
    Returns:
        Tuple (liste de features, stats de qualité)
    """
    features = []
    stats = {
        "total": len(transactions),
        "accepted": 0,
        "rejected": 0,
        "rejection_reasons": {
            "outliers": 0,
            "missing_price": 0,
            "missing_area": 0,
            "invalid_data": 0
        }
    }
    
    for tx in transactions:
        try:
            # Validation des données requises
            if not tx.get("price_aed") or float(tx["price_aed"]) <= 0:
                stats["rejected"] += 1
                stats["rejection_reasons"]["missing_price"] += 1
                continue
            
            if not tx.get("area_sqft") or float(tx["area_sqft"]) <= 0:
                stats["rejected"] += 1
                stats["rejection_reasons"]["missing_area"] += 1
                continue
            
            # Calculer ou récupérer prix/sqft
            price_per_sqft = tx.get("price_per_sqft")
            if not price_per_sqft:
                price_per_sqft = calculate_price_per_sqft(
                    Decimal(str(tx["price_aed"])),
                    Decimal(str(tx["area_sqft"]))
                )
            
            # Filtrer les outliers
            if price_per_sqft:
                psf_float = float(price_per_sqft)
                if psf_float < MIN_PRICE_PER_SQFT or psf_float > MAX_PRICE_PER_SQFT:
                    stats["rejected"] += 1
                    stats["rejection_reasons"]["outliers"] += 1
                    continue
            
            # Créer la feature
            feature = Feature(
                source_type="transaction",
                source_id=str(tx["transaction_id"]),
                record_date=tx["transaction_date"],
                
                community=normalize_location_name(tx.get("community")),
                project=normalize_location_name(tx.get("project")),
                building=normalize_location_name(tx.get("building")),
                rooms_bucket=tx.get("rooms_bucket"),
                property_type=tx.get("property_type"),
                
                price_aed=Decimal(str(tx["price_aed"])),
                price_per_sqft=Decimal(str(price_per_sqft)) if price_per_sqft else None,
                area_sqft=Decimal(str(tx["area_sqft"])),
                
                is_offplan=tx.get("is_offplan", False),
                days_on_market=None,
                price_change_count=0
            )
            
            features.append(feature)
            stats["accepted"] += 1
            
        except Exception as e:
            logger.warning(f"Erreur traitement transaction {tx.get('transaction_id')}: {e}")
            stats["rejected"] += 1
            stats["rejection_reasons"]["invalid_data"] += 1
    
    return features, stats


def _process_listings(listings: List[Dict]) -> Tuple[List[Feature], Dict]:
    """
    Traiter les listings et les convertir en features
    
    Returns:
        Tuple (liste de features, stats de qualité)
    """
    features = []
    stats = {
        "total": len(listings),
        "accepted": 0,
        "rejected": 0,
        "rejection_reasons": {
            "outliers": 0,
            "missing_price": 0,
            "missing_area": 0,
            "invalid_data": 0
        }
    }
    
    for listing in listings:
        try:
            # Validation des données requises
            if not listing.get("asking_price_aed") or float(listing["asking_price_aed"]) <= 0:
                stats["rejected"] += 1
                stats["rejection_reasons"]["missing_price"] += 1
                continue
            
            if not listing.get("area_sqft") or float(listing["area_sqft"]) <= 0:
                stats["rejected"] += 1
                stats["rejection_reasons"]["missing_area"] += 1
                continue
            
            # Calculer ou récupérer prix/sqft
            price_per_sqft = listing.get("asking_price_per_sqft")
            if not price_per_sqft:
                price_per_sqft = calculate_price_per_sqft(
                    Decimal(str(listing["asking_price_aed"])),
                    Decimal(str(listing["area_sqft"]))
                )
            
            # Filtrer les outliers
            if price_per_sqft:
                psf_float = float(price_per_sqft)
                if psf_float < MIN_PRICE_PER_SQFT or psf_float > MAX_PRICE_PER_SQFT:
                    stats["rejected"] += 1
                    stats["rejection_reasons"]["outliers"] += 1
                    continue
            
            # Créer la feature
            feature = Feature(
                source_type="listing",
                source_id=str(listing["listing_id"]),
                record_date=listing.get("listing_date") or date.today(),
                
                community=normalize_location_name(listing.get("community")),
                project=normalize_location_name(listing.get("project")),
                building=normalize_location_name(listing.get("building")),
                rooms_bucket=listing.get("rooms_bucket"),
                property_type=listing.get("property_type"),
                
                price_aed=Decimal(str(listing["asking_price_aed"])),
                price_per_sqft=Decimal(str(price_per_sqft)) if price_per_sqft else None,
                area_sqft=Decimal(str(listing["area_sqft"])),
                
                is_offplan=False,
                days_on_market=listing.get("days_on_market"),
                price_change_count=listing.get("price_changes", 0)
            )
            
            features.append(feature)
            stats["accepted"] += 1
            
        except Exception as e:
            logger.warning(f"Erreur traitement listing {listing.get('listing_id')}: {e}")
            stats["rejected"] += 1
            stats["rejection_reasons"]["invalid_data"] += 1
    
    return features, stats


def _enrich_with_makani(features: List[Feature]) -> List[Feature]:
    """
    Enrichir les features avec les données Makani (geo-features)
    
    Optimise les appels en batch et avec cache
    """
    if not features:
        return features
    
    logger.info(f"Enrichissement Makani pour {len(features)} features")
    
    try:
        makani_connector = MakaniGeocodingConnector()
        
        # Créer un cache pour éviter les appels dupliqués
        location_cache: Dict[str, dict] = {}
        
        for feature in features:
            # Clé de cache basée sur la localisation
            cache_key = f"{feature.community}|{feature.project}|{feature.building}"
            
            if cache_key not in location_cache:
                # Appel API Makani
                address = makani_connector.search_address(
                    community=feature.community,
                    project=feature.project,
                    building=feature.building
                )
                
                if address:
                    location_cache[cache_key] = {
                        "makani_number": address.makani_number,
                        "latitude": address.latitude,
                        "longitude": address.longitude,
                        "metro_distance_m": address.metro_distance_m,
                        "beach_distance_m": address.beach_distance_m,
                        "mall_distance_m": address.mall_distance_m,
                        "location_score": makani_connector.calculate_location_score(address)
                    }
                else:
                    location_cache[cache_key] = {}
            
            # Appliquer les données du cache
            geo_data = location_cache.get(cache_key, {})
            if geo_data:
                feature.makani_number = geo_data.get("makani_number")
                feature.latitude = geo_data.get("latitude")
                feature.longitude = geo_data.get("longitude")
                feature.metro_distance_m = geo_data.get("metro_distance_m")
                feature.beach_distance_m = geo_data.get("beach_distance_m")
                feature.mall_distance_m = geo_data.get("mall_distance_m")
                feature.location_score = Decimal(str(geo_data.get("location_score", 0)))
        
        logger.info(f"Enrichissement Makani terminé : {len(location_cache)} localisations uniques")
        
    except Exception as e:
        logger.warning(f"Erreur enrichissement Makani : {e}")
    
    return features


def _insert_features(features: List[Feature]) -> int:
    """Insérer les features dans la base de données"""
    if not features:
        return 0
    
    columns = [
        'source_type', 'source_id', 'record_date',
        'community', 'project', 'building', 'rooms_bucket', 'property_type',
        'price_aed', 'price_per_sqft', 'area_sqft',
        'is_offplan', 'days_on_market', 'price_change_count',
        'makani_number', 'latitude', 'longitude',
        'metro_distance_m', 'beach_distance_m', 'mall_distance_m', 'location_score'
    ]
    
    values = []
    for f in features:
        values.append((
            f.source_type,
            f.source_id,
            f.record_date,
            f.community,
            f.project,
            f.building,
            f.rooms_bucket,
            f.property_type,
            f.price_aed,
            f.price_per_sqft,
            f.area_sqft,
            f.is_offplan,
            f.days_on_market,
            f.price_change_count,
            f.makani_number,
            f.latitude,
            f.longitude,
            f.metro_distance_m,
            f.beach_distance_m,
            f.mall_distance_m,
            f.location_score
        ))
    
    try:
        # Utiliser UPSERT pour éviter les doublons
        query = f"""
        INSERT INTO features ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
        ON CONFLICT (source_type, source_id) DO UPDATE SET
            record_date = EXCLUDED.record_date,
            community = EXCLUDED.community,
            project = EXCLUDED.project,
            building = EXCLUDED.building,
            rooms_bucket = EXCLUDED.rooms_bucket,
            property_type = EXCLUDED.property_type,
            price_aed = EXCLUDED.price_aed,
            price_per_sqft = EXCLUDED.price_per_sqft,
            area_sqft = EXCLUDED.area_sqft,
            is_offplan = EXCLUDED.is_offplan,
            days_on_market = EXCLUDED.days_on_market,
            price_change_count = EXCLUDED.price_change_count,
            makani_number = EXCLUDED.makani_number,
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            metro_distance_m = EXCLUDED.metro_distance_m,
            beach_distance_m = EXCLUDED.beach_distance_m,
            mall_distance_m = EXCLUDED.mall_distance_m,
            location_score = EXCLUDED.location_score
        """
        
        db.execute_batch(query, values)
        return len(values)
        
    except Exception as e:
        logger.error(f"Erreur insertion features : {e}")
        return 0


def _merge_quality_stats(main_stats: Dict, source_stats: Dict, source_type: str):
    """Fusionner les stats de qualité"""
    main_stats["total"] += source_stats["total"]
    main_stats["accepted"] += source_stats["accepted"]
    main_stats["rejected"] += source_stats["rejected"]
    
    for reason, count in source_stats.get("rejection_reasons", {}).items():
        if reason in main_stats["rejection_reasons"]:
            main_stats["rejection_reasons"][reason] += count


def _calculate_field_completeness(features: List[Feature]) -> Dict[str, float]:
    """Calculer le taux de complétude par champ"""
    if not features:
        return {}
    
    total = len(features)
    fields = ["community", "project", "building", "rooms_bucket", "property_type",
              "price_aed", "price_per_sqft", "area_sqft", "location_score"]
    
    completeness = {}
    for field in fields:
        non_null = sum(1 for f in features if getattr(f, field, None) is not None)
        completeness[field] = round(non_null / total * 100, 1)
    
    return completeness


def _save_quality_log(quality_log: QualityLog):
    """Sauvegarder le log de qualité dans la base"""
    try:
        import json
        
        query = """
        INSERT INTO quality_logs (
            run_date, source_type, pipeline_step,
            records_total, records_accepted, records_rejected,
            rejection_reasons, field_completeness,
            execution_time_ms, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        db.execute_query(query, (
            quality_log.run_date,
            quality_log.source_type,
            quality_log.pipeline_step,
            quality_log.records_total,
            quality_log.records_accepted,
            quality_log.records_rejected,
            json.dumps(quality_log.rejection_reasons),
            json.dumps(quality_log.field_completeness),
            quality_log.execution_time_ms,
            quality_log.status
        ))
        
    except Exception as e:
        logger.warning(f"Erreur sauvegarde quality log : {e}")


if __name__ == "__main__":
    from core.utils import setup_logging
    setup_logging()
    
    count, quality = compute_features()
    print(f"Features calculées : {count}")
    print(f"Taux d'acceptation : {quality.records_accepted}/{quality.records_total}")
    print(f"Rejets : {quality.rejection_reasons}")
