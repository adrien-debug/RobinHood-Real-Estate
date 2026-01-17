"""
Refresher pour Streamlit
"""
from datetime import date
from typing import Dict, Any
from loguru import logger
from core.db import db
from realtime.cache import cache


class DataRefresher:
    """Gestionnaire de refresh des données pour Streamlit"""
    
    @staticmethod
    def get_dashboard_data(target_date: date = None) -> Dict[str, Any]:
        """Récupérer les données du dashboard avec cache"""
        if not target_date:
            from core.utils import get_dubai_today
            target_date = get_dubai_today()
        
        cache_key = f"dashboard_{target_date}"
        
        # Vérifier le cache
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Récupérer les données
        data = {
            'kpis': DataRefresher._get_kpis(target_date),
            'top_opportunities': DataRefresher._get_top_opportunities(target_date),
            'regimes': DataRefresher._get_regimes(target_date),
            'brief': DataRefresher._get_daily_brief(target_date)
        }
        
        # Mettre en cache
        cache.set(cache_key, data)
        
        return data
    
    @staticmethod
    def _get_kpis(target_date: date) -> Dict:
        """KPIs principaux"""
        query_tx = """
        SELECT COUNT(*) as count, AVG(price_per_sqft) as avg_price
        FROM dld_transactions
        WHERE transaction_date = %s
        """
        tx_data = db.execute_query(query_tx, (target_date,))
        
        query_opp = """
        SELECT COUNT(*) as count, AVG(global_score) as avg_score
        FROM dld_opportunities
        WHERE detection_date = %s AND status = 'active'
        """
        opp_data = db.execute_query(query_opp, (target_date,))
        
        return {
            'transactions_count': tx_data[0]['count'] if tx_data else 0,
            'avg_price_sqft': tx_data[0]['avg_price'] if tx_data else 0,
            'opportunities_count': opp_data[0]['count'] if opp_data else 0,
            'avg_opportunity_score': opp_data[0]['avg_score'] if opp_data else 0
        }
    
    @staticmethod
    def _get_top_opportunities(target_date: date, limit: int = 10) -> list:
        """Top opportunités"""
        query = """
        SELECT * FROM dld_opportunities
        WHERE detection_date = %s AND status = 'active'
        ORDER BY global_score DESC
        LIMIT %s
        """
        return db.execute_query(query, (target_date, limit))
    
    @staticmethod
    def _get_regimes(target_date: date) -> list:
        """Régimes de marché"""
        query = """
        SELECT * FROM dld_market_regimes
        WHERE regime_date = %s
        ORDER BY confidence_score DESC
        LIMIT 20
        """
        return db.execute_query(query, (target_date,))
    
    @staticmethod
    def _get_daily_brief(target_date: date) -> Dict:
        """Brief quotidien CIO"""
        query = """
        SELECT * FROM dld_daily_briefs
        WHERE brief_date = %s
        """
        results = db.execute_query(query, (target_date,))
        return results[0] if results else None
