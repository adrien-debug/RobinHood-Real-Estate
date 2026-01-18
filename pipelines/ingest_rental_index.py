"""
Pipeline : Ingestion de l'index locatif DLD

Récupère et stocke les données de loyers depuis l'API DLD Rental Index.
Essentiel pour :
- Calcul du RSG (Rental Stress Gap)
- Stratégie RENT
- Estimation des rendements locatifs
"""
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
from loguru import logger

from core.db import db
from core.models import RentalIndex
from core.utils import get_dubai_today
from connectors.dld_rental_index import DLDRentalIndexConnector
from pipelines.quality_logger import QualityLogger


def ingest_rental_index(period_date: Optional[date] = None) -> int:
    """
    Ingérer les données d'index locatif DLD
    
    Args:
        period_date: Date de la période (défaut: premier du mois courant)
        
    Returns:
        Nombre d'entrées insérées/mises à jour
    """
    if not period_date:
        period_date = get_dubai_today().replace(day=1)
    
    logger.info(f"Ingestion index locatif pour période : {period_date}")
    
    # Initialiser le logger de qualité
    qlogger = QualityLogger("rental_index", "ingestion")
    qlogger.start()
    
    # Récupérer les données via le connecteur
    connector = DLDRentalIndexConnector()
    rental_data = connector.fetch_rental_index(period_date)
    
    qlogger.add_total(len(rental_data))
    
    if not rental_data:
        logger.warning("Aucune donnée d'index locatif récupérée")
        qlogger.finish()
        return 0
    
    # Valider et filtrer les données
    valid_records = []
    field_stats = {
        "community": 0,
        "project": 0,
        "rooms_bucket": 0,
        "avg_rent_aed": 0,
        "median_rent_aed": 0,
        "rent_count": 0
    }
    
    for rental in rental_data:
        # Validation basique
        if not rental.community:
            qlogger.reject("missing_community")
            continue
        
        if not rental.avg_rent_aed and not rental.median_rent_aed:
            qlogger.reject("missing_rent_data")
            continue
        
        # Comptage des champs non-null
        if rental.community:
            field_stats["community"] += 1
        if rental.project:
            field_stats["project"] += 1
        if rental.rooms_bucket:
            field_stats["rooms_bucket"] += 1
        if rental.avg_rent_aed:
            field_stats["avg_rent_aed"] += 1
        if rental.median_rent_aed:
            field_stats["median_rent_aed"] += 1
        if rental.rent_count:
            field_stats["rent_count"] += 1
        
        valid_records.append(rental)
        qlogger.accept()
    
    # Calculer la complétude
    total = len(valid_records) if valid_records else 1
    completeness = {
        field: round(count / total * 100, 1)
        for field, count in field_stats.items()
    }
    qlogger.set_field_completeness(completeness)
    
    # Insérer en base
    inserted = _insert_rental_index(valid_records)
    
    # Finaliser le log
    qlogger.finish()
    
    logger.info(f"Index locatif ingéré : {inserted} entrées")
    return inserted


def _insert_rental_index(records: List[RentalIndex]) -> int:
    """Insérer les records d'index locatif en base"""
    if not records:
        return 0
    
    columns = [
        'period_date', 'community', 'project', 
        'property_type', 'rooms_bucket',
        'avg_rent_aed', 'median_rent_aed', 'rent_count'
    ]
    
    values = []
    for r in records:
        values.append((
            r.period_date,
            r.community,
            r.project,
            r.property_type,
            r.rooms_bucket,
            r.avg_rent_aed,
            r.median_rent_aed,
            r.rent_count
        ))
    
    try:
        # UPSERT pour éviter les doublons
        query = """
        INSERT INTO rental_index (
            period_date, community, project,
            property_type, rooms_bucket,
            avg_rent_aed, median_rent_aed, rent_count
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (period_date, community, project, property_type, rooms_bucket) 
        DO UPDATE SET
            avg_rent_aed = EXCLUDED.avg_rent_aed,
            median_rent_aed = EXCLUDED.median_rent_aed,
            rent_count = EXCLUDED.rent_count
        """
        
        db.execute_batch(query, values)
        return len(values)
        
    except Exception as e:
        logger.error(f"Erreur insertion rental index : {e}")
        return 0


def get_rental_data(
    community: str,
    rooms_bucket: Optional[str] = None,
    period_date: Optional[date] = None
) -> Optional[RentalIndex]:
    """
    Récupérer les données de loyer pour une zone
    
    Args:
        community: Nom de la communauté
        rooms_bucket: Type de chambres (optionnel)
        period_date: Date de période (défaut: dernier mois disponible)
        
    Returns:
        RentalIndex ou None
    """
    query = """
    SELECT 
        period_date, community, project,
        property_type, rooms_bucket,
        avg_rent_aed, median_rent_aed, rent_count
    FROM rental_index
    WHERE community = %s
    """
    params = [community]
    
    if rooms_bucket:
        query += " AND rooms_bucket = %s"
        params.append(rooms_bucket)
    
    if period_date:
        query += " AND period_date = %s"
        params.append(period_date)
    else:
        query += " ORDER BY period_date DESC LIMIT 1"
    
    try:
        results = db.execute_query(query, tuple(params))
        if results:
            row = results[0]
            return RentalIndex(
                period_date=row["period_date"],
                community=row["community"],
                project=row.get("project"),
                property_type=row.get("property_type"),
                rooms_bucket=row.get("rooms_bucket"),
                avg_rent_aed=row.get("avg_rent_aed"),
                median_rent_aed=row.get("median_rent_aed"),
                rent_count=row.get("rent_count")
            )
        return None
    except Exception as e:
        logger.error(f"Erreur récupération rental data : {e}")
        return None


def get_median_rent(
    community: str,
    rooms_bucket: Optional[str] = None
) -> Optional[Decimal]:
    """
    Récupérer le loyer médian pour une zone
    
    Args:
        community: Nom de la communauté
        rooms_bucket: Type de chambres (optionnel)
        
    Returns:
        Loyer médian annuel en AED ou None
    """
    rental = get_rental_data(community, rooms_bucket)
    if rental:
        return rental.median_rent_aed or rental.avg_rent_aed
    return None


def get_rental_yield_estimate(
    price_aed: Decimal,
    community: str,
    rooms_bucket: Optional[str] = None
) -> Optional[float]:
    """
    Estimer le rendement locatif pour un bien
    
    Args:
        price_aed: Prix d'achat en AED
        community: Communauté
        rooms_bucket: Type de chambres
        
    Returns:
        Rendement estimé en % (ex: 6.5 pour 6.5%)
    """
    if not price_aed or price_aed <= 0:
        return None
    
    rent = get_median_rent(community, rooms_bucket)
    if not rent:
        return None
    
    # Rendement = loyer annuel / prix * 100
    yield_pct = float(rent) / float(price_aed) * 100
    return round(yield_pct, 2)


if __name__ == "__main__":
    from core.utils import setup_logging
    setup_logging()
    
    count = ingest_rental_index()
    print(f"Index locatif ingéré : {count} entrées")
    
    # Test récupération
    rent = get_median_rent("Dubai Marina", "2BR")
    print(f"Loyer médian Dubai Marina 2BR : {rent} AED/an")
