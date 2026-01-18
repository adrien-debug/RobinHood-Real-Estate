"""
Pipeline : Calcul des scores multi-stratégies
"""
from datetime import date
from typing import Optional, Dict, List
from decimal import Decimal
from loguru import logger
from core.db import db
from strategies.flip import FlipStrategy
from strategies.rent import RentStrategy
from strategies.long_term import LongTermStrategy


def compute_scores(target_date: Optional[date] = None) -> int:
    """
    Calculer les scores pour toutes les opportunités détectées
    
    Returns:
        Nombre d'opportunités scorées
    """
    if not target_date:
        target_date = date.today()
    
    # Récupérer les anomalies détectées
    query = """
    SELECT * FROM detect_opportunities(%s)
    """
    anomalies = db.execute_query(query, (target_date,))
    
    if not anomalies:
        logger.info("Aucune opportunité à scorer")
        return 0
    
    # Initialiser les stratégies
    flip_strategy = FlipStrategy()
    rent_strategy = RentStrategy()
    long_term_strategy = LongTermStrategy()
    
    # Scorer chaque opportunité
    opportunities = []
    for anomaly in anomalies:
        try:
            # Contexte marché
            context = _get_market_context(
                anomaly['community'],
                anomaly.get('project'),
                anomaly.get('building'),
                anomaly['rooms_bucket'],
                target_date
            )
            
            # Calcul des scores par stratégie
            flip_score = flip_strategy.score(anomaly, context)
            rent_score = rent_strategy.score(anomaly, context)
            long_term_score = long_term_strategy.score(anomaly, context)
            
            # Score global (moyenne pondérée)
            global_score = (flip_score * 0.4 + rent_score * 0.3 + long_term_score * 0.3)
            
            # Recommandation
            scores_map = {
                'FLIP': flip_score,
                'RENT': rent_score,
                'LONG': long_term_score
            }
            recommended_strategy = max(scores_map, key=scores_map.get)
            
            # Si tous les scores sont faibles, ignorer
            if global_score < 40:
                recommended_strategy = 'IGNORE'
            
            opportunities.append({
                'detection_date': target_date,
                'transaction_id': anomaly['transaction_id'],
                'community': anomaly['community'],
                'project': anomaly.get('project'),
                'building': anomaly.get('building'),
                'rooms_bucket': anomaly['rooms_bucket'],
                'price_per_sqft': anomaly['price_per_sqft'],
                'market_median_sqft': anomaly['market_median_sqft'],
                'discount_pct': anomaly['discount_pct'],
                'global_score': round(global_score, 2),
                'flip_score': round(flip_score, 2),
                'rent_score': round(rent_score, 2),
                'long_term_score': round(long_term_score, 2),
                'recommended_strategy': recommended_strategy,
                'market_regime': context.get('regime'),
                'liquidity_score': context.get('liquidity_score'),
                'supply_risk': context.get('supply_risk'),
                'status': 'active'
            })
        except Exception as e:
            logger.warning(f"Erreur scoring opportunité : {e}")
            continue
    
    # Insérer dans la base
    if opportunities:
        columns = [
            'detection_date', 'transaction_id', 'community', 'project', 'building', 'rooms_bucket',
            'price_per_sqft', 'market_median_sqft', 'discount_pct',
            'global_score', 'flip_score', 'rent_score', 'long_term_score',
            'recommended_strategy', 'market_regime', 'liquidity_score', 'supply_risk', 'status'
        ]
        
        values = [
            (
                o['detection_date'], o['transaction_id'], o['community'], o['project'], o['building'], o['rooms_bucket'],
                o['price_per_sqft'], o['market_median_sqft'], o['discount_pct'],
                o['global_score'], o['flip_score'], o['rent_score'], o['long_term_score'],
                o['recommended_strategy'], o['market_regime'], o['liquidity_score'], o['supply_risk'], o['status']
            )
            for o in opportunities
        ]
        
        db.execute_batch_insert('opportunities', columns, values)
    
    logger.info(f"✅ Opportunités scorées : {len(opportunities)}")
    return len(opportunities)


def _get_market_context(
    community: str,
    project: Optional[str],
    building: Optional[str],
    rooms_bucket: str,
    target_date: date
) -> Dict:
    """Récupérer le contexte marché pour le scoring"""
    context = {}
    
    # Baseline 30j
    query_baseline = """
    SELECT * FROM market_baselines
    WHERE calculation_date = %s
        AND community = %s
        AND COALESCE(project, '') = COALESCE(%s, '')
        AND rooms_bucket = %s
        AND window_days = 30
    LIMIT 1
    """
    baseline = db.execute_query(query_baseline, (target_date, community, project, rooms_bucket))
    if baseline:
        context['baseline'] = baseline[0]
        context['liquidity_score'] = min(100, baseline[0].get('transaction_count', 0) * 5)
    else:
        context['liquidity_score'] = 0
    
    # Régime de marché
    query_regime = """
    SELECT * FROM market_regimes
    WHERE regime_date = %s
        AND community = %s
        AND COALESCE(project, '') = COALESCE(%s, '')
    LIMIT 1
    """
    regime = db.execute_query(query_regime, (target_date, community, project))
    if regime:
        context['regime'] = regime[0].get('regime')
        context['regime_confidence'] = regime[0].get('confidence_score')
    else:
        context['regime'] = 'NEUTRAL'
        context['regime_confidence'] = 0.5
    
    # Supply risk (à enrichir avec developers_pipeline)
    context['supply_risk'] = 'low'  # Placeholder
    
    return context


if __name__ == "__main__":
    from core.utils import setup_logging
    setup_logging()
    
    count = compute_scores()
    print(f"Opportunités scorées : {count}")
