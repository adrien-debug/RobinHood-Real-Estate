"""
Pipeline : Calcul des KPIs avancés

8 KPIs calculés pour chaque scope (community, project, rooms_bucket) et fenêtre (7/30/90 jours) :

1. TLS (Transaction-to-Listing Spread)
   = (median_listing_psf - median_tx_psf) / median_tx_psf
   
2. LAD (Liquidity-Adjusted Discount)
   = discount_pct * log(1 + tx_count_30d)
   
3. RSG (Rental Stress Gap)
   = (median_rent - expected_rent) / expected_rent
   expected_rent = price_psf * sqft * target_yield
   
4. SPI (Supply Pressure Index) - normalisé 0-100
   = normalize(planned_units_12m / tx_count_12m)
   
5. GPI (Geo-Premium Index)
   = location_score * (1 + observed_price_premium)
   
6. RCWM (Regime Confidence-Weighted Momentum)
   = momentum * regime_confidence
   
7. ORD (Offplan Risk Delta)
   = (median_offplan_psf / median_ready_psf) - 1
   
8. APS (Anomaly Persistence Score)
   = days_anomaly_active / window_days
"""
from datetime import date, timedelta
from typing import Optional, List, Dict, Tuple
from decimal import Decimal
import math
from loguru import logger

from core.db import db
from core.models import KPI
from core.utils import get_dubai_today
from pipelines.quality_logger import QualityLogger


# Seuil de rendement cible pour RSG
TARGET_YIELD = 0.06  # 6%

# Fenêtres de calcul
WINDOWS = [7, 30, 90]


def compute_kpis(target_date: Optional[date] = None) -> int:
    """
    Pipeline principal de calcul des KPIs
    
    Calcule les 8 KPIs pour toutes les combinaisons community/rooms_bucket
    sur les fenêtres 7, 30 et 90 jours.
    
    Args:
        target_date: Date cible (défaut: aujourd'hui)
        
    Returns:
        Nombre de KPIs insérés
    """
    if not target_date:
        target_date = get_dubai_today()
    
    logger.info(f"Calcul des KPIs pour {target_date}")
    
    # Logger qualité
    qlogger = QualityLogger("kpis", "compute_kpis")
    qlogger.start()
    
    # Récupérer les scopes uniques (community, rooms_bucket)
    scopes = _get_unique_scopes(target_date)
    qlogger.add_total(len(scopes) * len(WINDOWS))
    
    all_kpis = []
    
    for community, rooms_bucket in scopes:
        for window_days in WINDOWS:
            try:
                kpi = _compute_kpi_for_scope(
                    target_date, 
                    community, 
                    rooms_bucket, 
                    window_days
                )
                if kpi:
                    all_kpis.append(kpi)
                    qlogger.accept()
                else:
                    qlogger.reject("insufficient_data")
            except Exception as e:
                logger.warning(f"Erreur KPI {community}/{rooms_bucket}/{window_days}: {e}")
                qlogger.reject("computation_error")
    
    # Insérer les KPIs
    inserted = _insert_kpis(all_kpis)
    
    qlogger.finish()
    
    logger.info(f"KPIs calculés : {inserted}")
    return inserted


def _get_unique_scopes(target_date: date) -> List[Tuple[str, str]]:
    """Récupérer les combinaisons uniques community/rooms_bucket avec données récentes"""
    query = """
    SELECT DISTINCT community, rooms_bucket
    FROM features
    WHERE community IS NOT NULL
        AND rooms_bucket IS NOT NULL
        AND record_date >= %s - INTERVAL '90 days'
    ORDER BY community, rooms_bucket
    """
    try:
        results = db.execute_query(query, (target_date,))
        return [(r["community"], r["rooms_bucket"]) for r in (results or [])]
    except Exception as e:
        logger.error(f"Erreur récupération scopes : {e}")
        return []


def _compute_kpi_for_scope(
    target_date: date,
    community: str,
    rooms_bucket: str,
    window_days: int
) -> Optional[KPI]:
    """
    Calculer tous les KPIs pour un scope donné
    
    Args:
        target_date: Date de calcul
        community: Communauté
        rooms_bucket: Type de chambres
        window_days: Fenêtre en jours
        
    Returns:
        KPI ou None si données insuffisantes
    """
    # Récupérer les données sources
    tx_data = _get_transaction_stats(target_date, community, rooms_bucket, window_days)
    listing_data = _get_listing_stats(target_date, community, rooms_bucket)
    rental_data = _get_rental_stats(community, rooms_bucket)
    supply_data = _get_supply_data(community)
    regime_data = _get_regime_data(target_date, community)
    geo_data = _get_geo_stats(community, rooms_bucket)
    anomaly_data = _get_anomaly_stats(target_date, community, rooms_bucket, window_days)
    offplan_data = _get_offplan_stats(target_date, community, rooms_bucket, window_days)
    
    # Vérifier données minimales
    if not tx_data.get("tx_count") or tx_data["tx_count"] < 3:
        return None
    
    # Calculer chaque KPI
    tls = _calc_tls(tx_data.get("median_psf"), listing_data.get("median_psf"))
    lad = _calc_lad(tx_data.get("avg_discount_pct"), tx_data.get("tx_count"))
    rsg = _calc_rsg(
        rental_data.get("median_rent"), 
        tx_data.get("median_psf"),
        tx_data.get("avg_sqft")
    )
    spi = _calc_spi(supply_data.get("planned_units_12m"), tx_data.get("tx_count_12m"))
    gpi = _calc_gpi(geo_data.get("avg_location_score"), tx_data.get("price_premium"))
    rcwm = _calc_rcwm(tx_data.get("momentum"), regime_data.get("confidence"))
    ord_value = _calc_ord(offplan_data.get("median_offplan_psf"), offplan_data.get("median_ready_psf"))
    aps = _calc_aps(anomaly_data.get("days_active"), window_days)
    
    return KPI(
        calculation_date=target_date,
        community=community,
        project=None,
        rooms_bucket=rooms_bucket,
        window_days=window_days,
        
        tls=Decimal(str(round(tls, 4))) if tls is not None else None,
        lad=Decimal(str(round(lad, 4))) if lad is not None else None,
        rsg=Decimal(str(round(rsg, 4))) if rsg is not None else None,
        spi=Decimal(str(round(spi, 4))) if spi is not None else None,
        gpi=Decimal(str(round(gpi, 4))) if gpi is not None else None,
        rcwm=Decimal(str(round(rcwm, 4))) if rcwm is not None else None,
        ord=Decimal(str(round(ord_value, 4))) if ord_value is not None else None,
        aps=Decimal(str(round(aps, 4))) if aps is not None else None,
        
        median_tx_psf=tx_data.get("median_psf"),
        median_listing_psf=listing_data.get("median_psf"),
        tx_count=tx_data.get("tx_count"),
        listing_count=listing_data.get("listing_count"),
        planned_units_12m=supply_data.get("planned_units_12m"),
        median_rent_aed=rental_data.get("median_rent")
    )


# ====================================================================
# FONCTIONS DE RÉCUPÉRATION DES DONNÉES
# ====================================================================

def _get_transaction_stats(
    target_date: date, 
    community: str, 
    rooms_bucket: str, 
    window_days: int
) -> Dict:
    """Récupérer les stats de transactions"""
    query = """
    SELECT 
        COUNT(*) as tx_count,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_per_sqft) as median_psf,
        AVG(area_sqft) as avg_sqft
    FROM features
    WHERE source_type = 'transaction'
        AND community = %s
        AND rooms_bucket = %s
        AND record_date >= %s - INTERVAL '%s days'
        AND record_date <= %s
        AND price_per_sqft IS NOT NULL
    """
    
    try:
        results = db.execute_query(query, (community, rooms_bucket, target_date, window_days, target_date))
        if results:
            row = results[0]
            
            # Récupérer aussi les données 12 mois pour SPI
            query_12m = """
            SELECT COUNT(*) as tx_count_12m
            FROM features
            WHERE source_type = 'transaction'
                AND community = %s
                AND rooms_bucket = %s
                AND record_date >= %s - INTERVAL '365 days'
            """
            results_12m = db.execute_query(query_12m, (community, rooms_bucket, target_date))
            
            # Récupérer le momentum depuis market_baselines
            query_momentum = """
            SELECT momentum
            FROM market_baselines
            WHERE community = %s
                AND rooms_bucket = %s
                AND window_days = %s
            ORDER BY calculation_date DESC
            LIMIT 1
            """
            momentum_results = db.execute_query(query_momentum, (community, rooms_bucket, window_days))
            
            return {
                "tx_count": row.get("tx_count", 0),
                "median_psf": Decimal(str(row["median_psf"])) if row.get("median_psf") else None,
                "avg_sqft": Decimal(str(row["avg_sqft"])) if row.get("avg_sqft") else None,
                "tx_count_12m": results_12m[0]["tx_count_12m"] if results_12m else 0,
                "momentum": momentum_results[0]["momentum"] if momentum_results else None
            }
    except Exception as e:
        logger.warning(f"Erreur transaction stats : {e}")
    
    return {}


def _get_listing_stats(target_date: date, community: str, rooms_bucket: str) -> Dict:
    """Récupérer les stats de listings"""
    query = """
    SELECT 
        COUNT(*) as listing_count,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_per_sqft) as median_psf
    FROM features
    WHERE source_type = 'listing'
        AND community = %s
        AND rooms_bucket = %s
        AND record_date >= %s - INTERVAL '30 days'
        AND price_per_sqft IS NOT NULL
    """
    
    try:
        results = db.execute_query(query, (community, rooms_bucket, target_date))
        if results:
            row = results[0]
            return {
                "listing_count": row.get("listing_count", 0),
                "median_psf": Decimal(str(row["median_psf"])) if row.get("median_psf") else None
            }
    except Exception as e:
        logger.warning(f"Erreur listing stats : {e}")
    
    return {}


def _get_rental_stats(community: str, rooms_bucket: str) -> Dict:
    """Récupérer les stats de loyers"""
    query = """
    SELECT median_rent_aed, avg_rent_aed
    FROM rental_index
    WHERE community = %s
        AND rooms_bucket = %s
    ORDER BY period_date DESC
    LIMIT 1
    """
    
    try:
        results = db.execute_query(query, (community, rooms_bucket))
        if results:
            row = results[0]
            return {
                "median_rent": row.get("median_rent_aed") or row.get("avg_rent_aed")
            }
    except Exception as e:
        logger.warning(f"Erreur rental stats : {e}")
    
    return {}


def _get_supply_data(community: str) -> Dict:
    """Récupérer les données de supply future"""
    cutoff_12m = date.today() + timedelta(days=365)
    
    query = """
    SELECT 
        COALESCE(SUM(total_units), 0) as planned_units_12m
    FROM developers_pipeline
    WHERE community = %s
        AND expected_handover_date <= %s
        AND status != 'delivered'
    """
    
    try:
        results = db.execute_query(query, (community, cutoff_12m))
        if results:
            return {
                "planned_units_12m": results[0].get("planned_units_12m", 0)
            }
    except Exception as e:
        logger.warning(f"Erreur supply data : {e}")
    
    return {"planned_units_12m": 0}


def _get_regime_data(target_date: date, community: str) -> Dict:
    """Récupérer les données de régime de marché"""
    query = """
    SELECT regime, confidence_score
    FROM market_regimes
    WHERE community = %s
    ORDER BY regime_date DESC
    LIMIT 1
    """
    
    try:
        results = db.execute_query(query, (community,))
        if results:
            return {
                "regime": results[0].get("regime"),
                "confidence": results[0].get("confidence_score")
            }
    except Exception as e:
        logger.warning(f"Erreur regime data : {e}")
    
    return {"confidence": Decimal("0.5")}


def _get_geo_stats(community: str, rooms_bucket: str) -> Dict:
    """Récupérer les stats de localisation (Makani)"""
    query = """
    SELECT AVG(location_score) as avg_location_score
    FROM features
    WHERE community = %s
        AND rooms_bucket = %s
        AND location_score IS NOT NULL
    """
    
    try:
        results = db.execute_query(query, (community, rooms_bucket))
        if results and results[0].get("avg_location_score"):
            return {
                "avg_location_score": float(results[0]["avg_location_score"])
            }
    except Exception as e:
        logger.warning(f"Erreur geo stats : {e}")
    
    return {}


def _get_anomaly_stats(
    target_date: date, 
    community: str, 
    rooms_bucket: str, 
    window_days: int
) -> Dict:
    """Récupérer les stats d'anomalies actives"""
    query = """
    SELECT 
        COUNT(DISTINCT detection_date) as days_active
    FROM opportunities
    WHERE community = %s
        AND rooms_bucket = %s
        AND detection_date >= %s - INTERVAL '%s days'
        AND detection_date <= %s
        AND status = 'active'
    """
    
    try:
        results = db.execute_query(query, (community, rooms_bucket, target_date, window_days, target_date))
        if results:
            return {
                "days_active": results[0].get("days_active", 0)
            }
    except Exception as e:
        logger.warning(f"Erreur anomaly stats : {e}")
    
    return {}


def _get_offplan_stats(
    target_date: date, 
    community: str, 
    rooms_bucket: str, 
    window_days: int
) -> Dict:
    """Récupérer les stats offplan vs ready"""
    # Offplan
    query_offplan = """
    SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_per_sqft) as median_psf
    FROM features
    WHERE source_type = 'transaction'
        AND community = %s
        AND rooms_bucket = %s
        AND is_offplan = TRUE
        AND record_date >= %s - INTERVAL '%s days'
        AND price_per_sqft IS NOT NULL
    """
    
    # Ready
    query_ready = """
    SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_per_sqft) as median_psf
    FROM features
    WHERE source_type = 'transaction'
        AND community = %s
        AND rooms_bucket = %s
        AND is_offplan = FALSE
        AND record_date >= %s - INTERVAL '%s days'
        AND price_per_sqft IS NOT NULL
    """
    
    try:
        offplan = db.execute_query(query_offplan, (community, rooms_bucket, target_date, window_days))
        ready = db.execute_query(query_ready, (community, rooms_bucket, target_date, window_days))
        
        return {
            "median_offplan_psf": offplan[0]["median_psf"] if offplan and offplan[0].get("median_psf") else None,
            "median_ready_psf": ready[0]["median_psf"] if ready and ready[0].get("median_psf") else None
        }
    except Exception as e:
        logger.warning(f"Erreur offplan stats : {e}")
    
    return {}


# ====================================================================
# FONCTIONS DE CALCUL DES KPIs
# ====================================================================

def _calc_tls(median_tx_psf: Optional[Decimal], median_listing_psf: Optional[Decimal]) -> Optional[float]:
    """
    TLS (Transaction-to-Listing Spread)
    = (median_listing_psf - median_tx_psf) / median_tx_psf
    """
    if not median_tx_psf or not median_listing_psf or float(median_tx_psf) == 0:
        return None
    return (float(median_listing_psf) - float(median_tx_psf)) / float(median_tx_psf)


def _calc_lad(discount_pct: Optional[float], tx_count: Optional[int]) -> Optional[float]:
    """
    LAD (Liquidity-Adjusted Discount)
    = discount_pct * log(1 + tx_count)
    """
    if discount_pct is None or tx_count is None:
        return None
    return float(discount_pct) * math.log(1 + tx_count)


def _calc_rsg(
    median_rent: Optional[Decimal], 
    median_psf: Optional[Decimal],
    avg_sqft: Optional[Decimal]
) -> Optional[float]:
    """
    RSG (Rental Stress Gap)
    = (median_rent - expected_rent) / expected_rent
    expected_rent = price_psf * sqft * target_yield
    """
    if not median_rent or not median_psf or not avg_sqft:
        return None
    
    expected_rent = float(median_psf) * float(avg_sqft) * TARGET_YIELD
    if expected_rent == 0:
        return None
    
    return (float(median_rent) - expected_rent) / expected_rent


def _calc_spi(planned_units_12m: Optional[int], tx_count_12m: Optional[int]) -> Optional[float]:
    """
    SPI (Supply Pressure Index) - normalisé 0-100
    = normalize(planned_units_12m / tx_count_12m)
    """
    if tx_count_12m is None or tx_count_12m == 0:
        return 50.0  # Valeur neutre
    
    raw_ratio = (planned_units_12m or 0) / tx_count_12m
    # Normalisation : ratio de 2+ = 100, ratio de 0 = 0
    return min(100.0, max(0.0, raw_ratio * 50))


def _calc_gpi(avg_location_score: Optional[float], price_premium: Optional[float]) -> Optional[float]:
    """
    GPI (Geo-Premium Index)
    = location_score * (1 + observed_price_premium)
    """
    if avg_location_score is None:
        return None
    
    premium = price_premium or 0
    return avg_location_score * (1 + premium)


def _calc_rcwm(momentum: Optional[Decimal], confidence: Optional[Decimal]) -> Optional[float]:
    """
    RCWM (Regime Confidence-Weighted Momentum)
    = momentum * regime_confidence
    """
    if momentum is None or confidence is None:
        return None
    return float(momentum) * float(confidence)


def _calc_ord(median_offplan_psf: Optional[Decimal], median_ready_psf: Optional[Decimal]) -> Optional[float]:
    """
    ORD (Offplan Risk Delta)
    = (median_offplan_psf / median_ready_psf) - 1
    """
    if not median_offplan_psf or not median_ready_psf or float(median_ready_psf) == 0:
        return None
    return (float(median_offplan_psf) / float(median_ready_psf)) - 1


def _calc_aps(days_active: Optional[int], window_days: int) -> Optional[float]:
    """
    APS (Anomaly Persistence Score)
    = days_anomaly_active / window_days
    """
    if window_days == 0:
        return None
    return (days_active or 0) / window_days


# ====================================================================
# INSERTION EN BASE
# ====================================================================

def _insert_kpis(kpis: List[KPI]) -> int:
    """Insérer les KPIs en base de données"""
    if not kpis:
        return 0
    
    columns = [
        'calculation_date', 'community', 'project', 'rooms_bucket', 'window_days',
        'tls', 'lad', 'rsg', 'spi', 'gpi', 'rcwm', 'ord', 'aps',
        'median_tx_psf', 'median_listing_psf', 'tx_count', 'listing_count',
        'planned_units_12m', 'median_rent_aed'
    ]
    
    values = []
    for k in kpis:
        values.append((
            k.calculation_date,
            k.community,
            k.project,
            k.rooms_bucket,
            k.window_days,
            k.tls,
            k.lad,
            k.rsg,
            k.spi,
            k.gpi,
            k.rcwm,
            k.ord,
            k.aps,
            k.median_tx_psf,
            k.median_listing_psf,
            k.tx_count,
            k.listing_count,
            k.planned_units_12m,
            k.median_rent_aed
        ))
    
    try:
        query = f"""
        INSERT INTO kpis ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
        ON CONFLICT (calculation_date, community, project, rooms_bucket, window_days)
        DO UPDATE SET
            tls = EXCLUDED.tls,
            lad = EXCLUDED.lad,
            rsg = EXCLUDED.rsg,
            spi = EXCLUDED.spi,
            gpi = EXCLUDED.gpi,
            rcwm = EXCLUDED.rcwm,
            ord = EXCLUDED.ord,
            aps = EXCLUDED.aps,
            median_tx_psf = EXCLUDED.median_tx_psf,
            median_listing_psf = EXCLUDED.median_listing_psf,
            tx_count = EXCLUDED.tx_count,
            listing_count = EXCLUDED.listing_count,
            planned_units_12m = EXCLUDED.planned_units_12m,
            median_rent_aed = EXCLUDED.median_rent_aed
        """
        
        db.execute_batch(query, values)
        return len(values)
        
    except Exception as e:
        logger.error(f"Erreur insertion KPIs : {e}")
        return 0


# ====================================================================
# FONCTIONS UTILITAIRES D'ACCÈS AUX KPIs
# ====================================================================

def get_latest_kpis(
    community: str,
    rooms_bucket: Optional[str] = None,
    window_days: int = 30
) -> Optional[KPI]:
    """
    Récupérer les KPIs les plus récents pour un scope
    
    Args:
        community: Communauté
        rooms_bucket: Type de chambres (optionnel)
        window_days: Fenêtre en jours
        
    Returns:
        KPI ou None
    """
    query = """
    SELECT *
    FROM kpis
    WHERE community = %s
        AND window_days = %s
    """
    params = [community, window_days]
    
    if rooms_bucket:
        query += " AND rooms_bucket = %s"
        params.append(rooms_bucket)
    
    query += " ORDER BY calculation_date DESC LIMIT 1"
    
    try:
        results = db.execute_query(query, tuple(params))
        if results:
            row = results[0]
            return KPI(
                calculation_date=row["calculation_date"],
                community=row["community"],
                project=row.get("project"),
                rooms_bucket=row.get("rooms_bucket"),
                window_days=row["window_days"],
                tls=row.get("tls"),
                lad=row.get("lad"),
                rsg=row.get("rsg"),
                spi=row.get("spi"),
                gpi=row.get("gpi"),
                rcwm=row.get("rcwm"),
                ord=row.get("ord"),
                aps=row.get("aps"),
                median_tx_psf=row.get("median_tx_psf"),
                median_listing_psf=row.get("median_listing_psf"),
                tx_count=row.get("tx_count"),
                listing_count=row.get("listing_count"),
                planned_units_12m=row.get("planned_units_12m"),
                median_rent_aed=row.get("median_rent_aed")
            )
    except Exception as e:
        logger.error(f"Erreur récupération KPIs : {e}")
    
    return None


if __name__ == "__main__":
    from core.utils import setup_logging
    setup_logging()
    
    count = compute_kpis()
    print(f"KPIs calculés : {count}")
    
    # Test récupération
    kpis = get_latest_kpis("Dubai Marina", "2BR", 30)
    if kpis:
        print(f"TLS: {kpis.tls}, SPI: {kpis.spi}, RSG: {kpis.rsg}")
