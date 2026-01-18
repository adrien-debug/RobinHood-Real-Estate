"""
Règles d'alertes
"""
from typing import List, Dict
from datetime import date
from loguru import logger
from core.db import db


class AlertRules:
    """Règles de déclenchement d'alertes"""
    
    @staticmethod
    def check_high_discount_opportunities(target_date: date, threshold: float = 20.0) -> List[Dict]:
        """Alertes : opportunités avec discount élevé"""
        query = """
        SELECT id, community, building, rooms_bucket,
               discount_pct, global_score, recommended_strategy
        FROM dld_opportunities
        WHERE detection_date = %s
            AND discount_pct >= %s
            AND status = 'active'
        ORDER BY discount_pct DESC
        """
        
        results = db.execute_query(query, (target_date, threshold))
        
        alerts = []
        for opp in results:
            alerts.append({
                'alert_type': 'high_discount',
                'severity': 'high' if opp['discount_pct'] >= 30 else 'medium',
                'title': f"Opportunité {opp['discount_pct']:.1f}% sous marché",
                'message': (
                    f"{opp['community']} / {opp['building']} ({opp['rooms_bucket']}) : "
                    f"{opp['discount_pct']:.1f}% sous marché, "
                    f"score {opp['global_score']:.0f}, "
                    f"stratégie {opp['recommended_strategy']}"
                ),
                'opportunity_id': opp['id'],
                'community': opp['community']
            })
        
        logger.info(f"Alertes high_discount : {len(alerts)}")
        return alerts
    
    @staticmethod
    def check_regime_changes(target_date: date) -> List[Dict]:
        """Alertes : changements de régime de marché"""
        query = """
        SELECT 
            mr_today.community,
            mr_today.regime as current_regime,
            mr_yesterday.regime as previous_regime,
            mr_today.confidence_score
        FROM dld_market_regimes mr_today
        LEFT JOIN dld_market_regimes mr_yesterday ON
            mr_today.community = mr_yesterday.community
            AND mr_yesterday.regime_date = %s - INTERVAL '1 day'
        WHERE mr_today.regime_date = %s
            AND mr_today.regime != COALESCE(mr_yesterday.regime, 'NEUTRAL')
            AND mr_today.confidence_score >= 0.7
        """
        
        results = db.execute_query(query, (target_date, target_date))
        
        alerts = []
        for change in results:
            severity = 'high' if change['current_regime'] in ['RETOURNEMENT', 'EXPANSION'] else 'medium'
            
            alerts.append({
                'alert_type': 'regime_change',
                'severity': severity,
                'title': f"Changement de régime : {change['community']}",
                'message': (
                    f"{change['community']} : "
                    f"{change.get('previous_regime', 'N/A')} → {change['current_regime']} "
                    f"(confiance {change['confidence_score']:.2f})"
                ),
                'opportunity_id': None,
                'community': change['community']
            })
        
        logger.info(f"Alertes regime_change : {len(alerts)}")
        return alerts
    
    @staticmethod
    def check_high_volume_zones(target_date: date, min_transactions: int = 20) -> List[Dict]:
        """Alertes : zones avec volume élevé de transactions"""
        query = """
        SELECT community, COUNT(*) as tx_count, AVG(price_per_sqft) as avg_price
        FROM dld_transactions
        WHERE transaction_date = %s
        GROUP BY community
        HAVING COUNT(*) >= %s
        ORDER BY tx_count DESC
        """
        
        results = db.execute_query(query, (target_date, min_transactions))
        
        alerts = []
        for zone in results:
            alerts.append({
                'alert_type': 'high_volume',
                'severity': 'low',
                'title': f"Volume élevé : {zone['community']}",
                'message': (
                    f"{zone['community']} : {zone['tx_count']} transactions, "
                    f"prix moyen {zone['avg_price']:.0f} AED/sqft"
                ),
                'opportunity_id': None,
                'community': zone['community']
            })
        
        logger.info(f"Alertes high_volume : {len(alerts)}")
        return alerts
    
    @staticmethod
    def get_all_alerts(target_date: date) -> List[Dict]:
        """Récupérer toutes les alertes pour une date"""
        alerts = []
        
        # High discount
        alerts.extend(AlertRules.check_high_discount_opportunities(target_date))
        
        # Regime changes
        alerts.extend(AlertRules.check_regime_changes(target_date))
        
        # High volume (optionnel, peut être bruyant)
        # alerts.extend(AlertRules.check_high_volume_zones(target_date))
        
        return alerts
