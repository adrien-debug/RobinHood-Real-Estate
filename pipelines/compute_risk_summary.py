"""
Pipeline : Calcul du résumé des risques

Évalue 3 types de risques par zone :
1. Supply Risk : basé sur SPI (Supply Pressure Index)
2. Volatility Risk : basé sur volatilité des prix
3. Divergence Risk : basé sur TLS (écart listing/transaction)

Seuils :
- Supply : SPI < 30 = LOW, 30-70 = MEDIUM, > 70 = HIGH
- Volatilité : < 0.15 = LOW, 0.15-0.25 = MEDIUM, > 0.25 = HIGH
- Divergence : TLS < 0.10 = LOW, 0.10-0.20 = MEDIUM, > 0.20 = HIGH
"""
from datetime import date
from typing import Optional, List, Dict
from decimal import Decimal
import json
from loguru import logger

from core.db import db
from core.models import RiskSummary
from core.utils import get_dubai_today
from pipelines.quality_logger import QualityLogger


# Seuils de risque
SUPPLY_THRESHOLDS = {"low": 30, "high": 70}
VOLATILITY_THRESHOLDS = {"low": 0.15, "high": 0.25}
DIVERGENCE_THRESHOLDS = {"low": 0.10, "high": 0.20}


def compute_risk_summary(target_date: Optional[date] = None) -> int:
    """
    Pipeline de calcul des résumés de risques par zone
    
    Args:
        target_date: Date cible (défaut: aujourd'hui)
        
    Returns:
        Nombre de résumés créés
    """
    if not target_date:
        target_date = get_dubai_today()
    
    logger.info(f"Calcul des résumés de risques pour {target_date}")
    
    # Logger qualité
    qlogger = QualityLogger("risk_summaries", "compute_risk_summary")
    qlogger.start()
    
    # Récupérer les communautés uniques
    communities = _get_communities_with_data(target_date)
    qlogger.add_total(len(communities))
    
    summaries = []
    
    for community in communities:
        try:
            summary = _compute_risk_for_community(target_date, community)
            if summary:
                summaries.append(summary)
                qlogger.accept()
            else:
                qlogger.reject("insufficient_data")
        except Exception as e:
            logger.warning(f"Erreur risk summary {community}: {e}")
            qlogger.reject("computation_error")
    
    # Insérer les résumés
    inserted = _insert_risk_summaries(summaries)
    
    qlogger.finish()
    
    logger.info(f"Résumés de risques créés : {inserted}")
    return inserted


def _get_communities_with_data(target_date: date) -> List[str]:
    """Récupérer les communautés avec des KPIs récents"""
    query = """
    SELECT DISTINCT community
    FROM kpis
    WHERE calculation_date >= %s - INTERVAL '7 days'
        AND community IS NOT NULL
    ORDER BY community
    """
    try:
        results = db.execute_query(query, (target_date,))
        return [r["community"] for r in (results or [])]
    except Exception as e:
        logger.error(f"Erreur récupération communities : {e}")
        return []


def _compute_risk_for_community(target_date: date, community: str) -> Optional[RiskSummary]:
    """
    Calculer le résumé des risques pour une communauté
    
    Args:
        target_date: Date de calcul
        community: Nom de la communauté
        
    Returns:
        RiskSummary ou None
    """
    # Récupérer les KPIs (fenêtre 30 jours)
    kpi_data = _get_kpi_data(community)
    
    # Récupérer la volatilité
    volatility_data = _get_volatility_data(community)
    
    if not kpi_data and not volatility_data:
        return None
    
    # Calculer les niveaux de risque
    supply_spi = kpi_data.get("spi")
    supply_risk = _classify_risk(supply_spi, SUPPLY_THRESHOLDS)
    
    volatility = volatility_data.get("volatility")
    volatility_risk = _classify_risk(volatility, VOLATILITY_THRESHOLDS)
    
    tls = kpi_data.get("tls")
    # TLS peut être négatif (listing < transaction), on prend la valeur absolue
    tls_abs = abs(float(tls)) if tls is not None else None
    divergence_risk = _classify_risk(tls_abs, DIVERGENCE_THRESHOLDS)
    
    # Calculer le score global de risque (0-100)
    overall_score = _compute_overall_risk_score(
        supply_risk, volatility_risk, divergence_risk
    )
    
    # Générer les facteurs de risque
    risk_factors = _generate_risk_factors(
        supply_risk, supply_spi,
        volatility_risk, volatility,
        divergence_risk, tls
    )
    
    return RiskSummary(
        summary_date=target_date,
        community=community,
        project=None,
        
        supply_risk_level=supply_risk,
        volatility_risk_level=volatility_risk,
        divergence_risk_level=divergence_risk,
        
        supply_spi=Decimal(str(supply_spi)) if supply_spi is not None else None,
        volatility_pct=Decimal(str(volatility)) if volatility is not None else None,
        listing_tx_divergence_pct=Decimal(str(tls)) if tls is not None else None,
        
        overall_risk_score=Decimal(str(overall_score)),
        risk_factors=risk_factors
    )


def _get_kpi_data(community: str) -> Dict:
    """Récupérer les KPIs pour une communauté"""
    query = """
    SELECT 
        AVG(spi) as spi,
        AVG(tls) as tls
    FROM kpis
    WHERE community = %s
        AND window_days = 30
    ORDER BY calculation_date DESC
    LIMIT 1
    """
    try:
        results = db.execute_query(query, (community,))
        if results and results[0]:
            return {
                "spi": float(results[0]["spi"]) if results[0].get("spi") else None,
                "tls": float(results[0]["tls"]) if results[0].get("tls") else None
            }
    except Exception as e:
        logger.warning(f"Erreur récupération KPI data : {e}")
    return {}


def _get_volatility_data(community: str) -> Dict:
    """Récupérer la volatilité depuis les baselines"""
    query = """
    SELECT AVG(volatility) as volatility
    FROM market_baselines
    WHERE community = %s
        AND window_days = 30
    ORDER BY calculation_date DESC
    LIMIT 1
    """
    try:
        results = db.execute_query(query, (community,))
        if results and results[0]:
            return {
                "volatility": float(results[0]["volatility"]) if results[0].get("volatility") else None
            }
    except Exception as e:
        logger.warning(f"Erreur récupération volatility : {e}")
    return {}


def _classify_risk(value: Optional[float], thresholds: Dict[str, float]) -> str:
    """
    Classifier une valeur en niveau de risque
    
    Args:
        value: Valeur à classifier
        thresholds: Dict avec 'low' et 'high'
        
    Returns:
        'LOW', 'MEDIUM', 'HIGH' ou 'UNKNOWN'
    """
    if value is None:
        return "UNKNOWN"
    
    if value < thresholds["low"]:
        return "LOW"
    elif value <= thresholds["high"]:
        return "MEDIUM"
    else:
        return "HIGH"


def _compute_overall_risk_score(
    supply_risk: str,
    volatility_risk: str,
    divergence_risk: str
) -> float:
    """
    Calculer le score global de risque (0-100)
    
    Pondération :
    - Supply : 40%
    - Volatilité : 35%
    - Divergence : 25%
    """
    risk_values = {
        "LOW": 20,
        "MEDIUM": 50,
        "HIGH": 85,
        "UNKNOWN": 50
    }
    
    supply_score = risk_values.get(supply_risk, 50)
    volatility_score = risk_values.get(volatility_risk, 50)
    divergence_score = risk_values.get(divergence_risk, 50)
    
    overall = (
        supply_score * 0.40 +
        volatility_score * 0.35 +
        divergence_score * 0.25
    )
    
    return round(overall, 2)


def _generate_risk_factors(
    supply_risk: str, supply_spi: Optional[float],
    volatility_risk: str, volatility: Optional[float],
    divergence_risk: str, tls: Optional[float]
) -> List[str]:
    """Générer la liste des facteurs de risque identifiés"""
    factors = []
    
    if supply_risk == "HIGH":
        units = int(supply_spi * 10) if supply_spi else 0
        factors.append(f"High supply pressure (SPI: {supply_spi:.1f}) - {units}+ new units expected")
    elif supply_risk == "MEDIUM":
        factors.append(f"Moderate supply pressure (SPI: {supply_spi:.1f})")
    
    if volatility_risk == "HIGH":
        vol_pct = volatility * 100 if volatility else 0
        factors.append(f"High price volatility ({vol_pct:.1f}%)")
    elif volatility_risk == "MEDIUM":
        vol_pct = volatility * 100 if volatility else 0
        factors.append(f"Moderate price volatility ({vol_pct:.1f}%)")
    
    if divergence_risk == "HIGH":
        if tls and tls > 0:
            factors.append(f"Listings priced {abs(tls)*100:.1f}% above transactions - sellers overconfident")
        elif tls and tls < 0:
            factors.append(f"Listings priced {abs(tls)*100:.1f}% below transactions - distressed sales")
    elif divergence_risk == "MEDIUM":
        factors.append(f"Moderate listing/transaction spread ({tls*100:.1f}%)")
    
    return factors


def _insert_risk_summaries(summaries: List[RiskSummary]) -> int:
    """Insérer les résumés de risques en base"""
    if not summaries:
        return 0
    
    columns = [
        'summary_date', 'community', 'project',
        'supply_risk_level', 'volatility_risk_level', 'divergence_risk_level',
        'supply_spi', 'volatility_pct', 'listing_tx_divergence_pct',
        'overall_risk_score', 'risk_factors'
    ]
    
    values = []
    for s in summaries:
        values.append((
            s.summary_date,
            s.community,
            s.project,
            s.supply_risk_level,
            s.volatility_risk_level,
            s.divergence_risk_level,
            s.supply_spi,
            s.volatility_pct,
            s.listing_tx_divergence_pct,
            s.overall_risk_score,
            json.dumps(s.risk_factors)
        ))
    
    try:
        query = f"""
        INSERT INTO risk_summaries ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
        ON CONFLICT (summary_date, community, project)
        DO UPDATE SET
            supply_risk_level = EXCLUDED.supply_risk_level,
            volatility_risk_level = EXCLUDED.volatility_risk_level,
            divergence_risk_level = EXCLUDED.divergence_risk_level,
            supply_spi = EXCLUDED.supply_spi,
            volatility_pct = EXCLUDED.volatility_pct,
            listing_tx_divergence_pct = EXCLUDED.listing_tx_divergence_pct,
            overall_risk_score = EXCLUDED.overall_risk_score,
            risk_factors = EXCLUDED.risk_factors
        """
        
        db.execute_batch(query, values)
        return len(values)
        
    except Exception as e:
        logger.error(f"Erreur insertion risk summaries : {e}")
        return 0


# ====================================================================
# FONCTIONS D'ACCÈS AUX RISQUES
# ====================================================================

def get_high_risk_zones(min_score: float = 70) -> List[RiskSummary]:
    """
    Récupérer les zones à haut risque
    
    Args:
        min_score: Score minimum de risque
        
    Returns:
        Liste de RiskSummary triés par score décroissant
    """
    query = """
    SELECT *
    FROM risk_summaries
    WHERE summary_date = CURRENT_DATE
        AND overall_risk_score >= %s
    ORDER BY overall_risk_score DESC
    """
    
    try:
        results = db.execute_query(query, (min_score,))
        return [_row_to_risk_summary(r) for r in (results or [])]
    except Exception as e:
        logger.error(f"Erreur récupération high risk zones : {e}")
        return []


def get_risk_summary(community: str, target_date: Optional[date] = None) -> Optional[RiskSummary]:
    """
    Récupérer le résumé des risques pour une communauté
    
    Args:
        community: Nom de la communauté
        target_date: Date (défaut: aujourd'hui)
        
    Returns:
        RiskSummary ou None
    """
    if not target_date:
        target_date = get_dubai_today()
    
    query = """
    SELECT *
    FROM risk_summaries
    WHERE community = %s
        AND summary_date = %s
    LIMIT 1
    """
    
    try:
        results = db.execute_query(query, (community, target_date))
        if results:
            return _row_to_risk_summary(results[0])
    except Exception as e:
        logger.error(f"Erreur récupération risk summary : {e}")
    return None


def _row_to_risk_summary(row: Dict) -> RiskSummary:
    """Convertir une row DB en RiskSummary"""
    risk_factors = row.get("risk_factors", [])
    if isinstance(risk_factors, str):
        risk_factors = json.loads(risk_factors)
    
    return RiskSummary(
        summary_date=row["summary_date"],
        community=row["community"],
        project=row.get("project"),
        supply_risk_level=row.get("supply_risk_level", "UNKNOWN"),
        volatility_risk_level=row.get("volatility_risk_level", "UNKNOWN"),
        divergence_risk_level=row.get("divergence_risk_level", "UNKNOWN"),
        supply_spi=row.get("supply_spi"),
        volatility_pct=row.get("volatility_pct"),
        listing_tx_divergence_pct=row.get("listing_tx_divergence_pct"),
        overall_risk_score=row.get("overall_risk_score"),
        risk_factors=risk_factors
    )


if __name__ == "__main__":
    from core.utils import setup_logging
    setup_logging()
    
    count = compute_risk_summary()
    print(f"Résumés de risques créés : {count}")
    
    # Afficher les zones à haut risque
    high_risk = get_high_risk_zones(60)
    for zone in high_risk:
        print(f"{zone.community}: {zone.overall_risk_score} ({', '.join(zone.risk_factors)})")
