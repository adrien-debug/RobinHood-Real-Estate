"""
Refresher pour Streamlit - Dashboard Data Provider

Fournit les données pour le dashboard avec cache intelligent.
Fallback sur API live si base de données vide.
"""
from datetime import date, timedelta
from typing import Dict, Any, List
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
        
        # Récupérer les données enrichies
        kpis = DataRefresher._get_kpis(target_date)
        
        # Si pas de données DB, essayer l'API live
        if (kpis.get('transactions_30d') or 0) == 0:
            logger.info("Base vide - récupération données API live")
            live_data = DataRefresher._get_live_api_data(target_date)
            if live_data:
                cache.set(cache_key, live_data, ttl=300)  # Cache 5 min pour API
                return live_data
        
        data = {
            'kpis': kpis,
            'transaction_stats': DataRefresher._get_transaction_stats(target_date),
            'top_neighborhoods': DataRefresher._get_top_neighborhoods(target_date),
            'property_types': DataRefresher._get_property_types_breakdown(target_date),
            'top_opportunities': DataRefresher._get_top_opportunities(target_date),
            'regimes': DataRefresher._get_regimes(target_date),
            'brief': DataRefresher._get_daily_brief(target_date)
        }
        
        # Mettre en cache
        cache.set(cache_key, data)
        
        return data
    
    @staticmethod
    def _get_live_api_data(target_date: date) -> Dict[str, Any]:
        """Récupérer les données directement depuis l'API Bayut"""
        try:
            from connectors.dld_transactions import DLDTransactionsConnector
            from collections import defaultdict
            
            connector = DLDTransactionsConnector()
            
            # Récupérer 30 jours de transactions
            end_date = target_date
            start_date = target_date - timedelta(days=30)
            
            transactions = connector.fetch_transactions(start_date, end_date)
            
            if not transactions:
                logger.warning("Aucune transaction récupérée depuis l'API")
                return None
            
            logger.info(f"API live: {len(transactions)} transactions récupérées")
            
            # Calculer les KPIs depuis les données API
            tx_today = [t for t in transactions if t.transaction_date == target_date]
            tx_7d = [t for t in transactions if t.transaction_date >= target_date - timedelta(days=7)]
            tx_30d = transactions
            
            # Prix moyen et médian
            prices = [t.price_per_sqft for t in tx_30d if t.price_per_sqft and t.price_per_sqft > 0]
            avg_price = sum(prices) / len(prices) if prices else 0
            median_price = sorted(prices)[len(prices)//2] if prices else 0
            
            # Volume total
            volumes = [float(t.price_aed) for t in tx_30d if t.price_aed]
            total_volume = sum(volumes)
            
            # Top neighborhoods
            neighborhood_stats = defaultdict(lambda: {'count': 0, 'prices': [], 'volume': 0})
            for t in tx_30d:
                if t.community:
                    neighborhood_stats[t.community]['count'] += 1
                    if t.price_per_sqft and t.price_per_sqft > 0:
                        neighborhood_stats[t.community]['prices'].append(t.price_per_sqft)
                    if t.price_aed:
                        neighborhood_stats[t.community]['volume'] += float(t.price_aed)
            
            top_neighborhoods = []
            for community, stats in sorted(neighborhood_stats.items(), key=lambda x: x[1]['count'], reverse=True)[:10]:
                prices_list = stats['prices']
                top_neighborhoods.append({
                    'community': community,
                    'transaction_count': stats['count'],
                    'avg_price_sqft': sum(prices_list) / len(prices_list) if prices_list else 0,
                    'median_price_sqft': sorted(prices_list)[len(prices_list)//2] if prices_list else 0,
                    'total_volume': stats['volume'],
                    'avg_area': 0
                })
            
            # Property types (rooms_bucket)
            rooms_stats = defaultdict(lambda: {'count': 0, 'prices': [], 'volume': 0})
            for t in tx_30d:
                bucket = t.rooms_bucket or 'Unknown'
                rooms_stats[bucket]['count'] += 1
                if t.price_per_sqft and t.price_per_sqft > 0:
                    rooms_stats[bucket]['prices'].append(t.price_per_sqft)
                if t.price_aed:
                    rooms_stats[bucket]['volume'] += float(t.price_aed)
            
            by_rooms = []
            for bucket, stats in sorted(rooms_stats.items(), key=lambda x: x[1]['count'], reverse=True):
                prices_list = stats['prices']
                by_rooms.append({
                    'rooms_bucket': bucket,
                    'count': stats['count'],
                    'avg_price_sqft': sum(prices_list) / len(prices_list) if prices_list else 0,
                    'avg_price': stats['volume'] / stats['count'] if stats['count'] else 0,
                    'total_volume': stats['volume']
                })
            
            # Variation 7J vs semaine précédente
            tx_prev_7d = [t for t in transactions 
                         if target_date - timedelta(days=14) <= t.transaction_date < target_date - timedelta(days=7)]
            variation = ((len(tx_7d) - len(tx_prev_7d)) / len(tx_prev_7d) * 100) if tx_prev_7d else 0
            
            return {
                'kpis': {
                    'transactions_today': len(tx_today),
                    'transactions_7d': len(tx_7d),
                    'transactions_30d': len(tx_30d),
                    'volume_today': sum(float(t.price_aed) for t in tx_today if t.price_aed),
                    'volume_7d': sum(float(t.price_aed) for t in tx_7d if t.price_aed),
                    'volume_30d': total_volume,
                    'avg_price_sqft': avg_price,
                    'median_price_sqft': median_price,
                    'variation_7d_pct': variation,
                    'opportunities_count': 0,
                    'avg_opportunity_score': 0,
                    'transactions_count': len(tx_30d)
                },
                'transaction_stats': {'daily_transactions': [], 'total_days': 30},
                'top_neighborhoods': top_neighborhoods,
                'property_types': {
                    'by_rooms': by_rooms,
                    'by_type': [],
                    'by_offplan': []
                },
                'top_opportunities': [],
                'regimes': [],
                'brief': None,
                'data_source': 'API_LIVE'
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération API live: {e}")
            return None
    
    @staticmethod
    def _get_kpis(target_date: date) -> Dict:
        """KPIs principaux enrichis"""
        # Transactions aujourd'hui
        query_today = """
        SELECT COUNT(*) as count, 
               COALESCE(AVG(price_per_sqft), 0) as avg_price,
               COALESCE(SUM(price_aed), 0) as volume
        FROM transactions
        WHERE transaction_date = %s
        """
        today_data = db.execute_query(query_today, (target_date,))
        
        # Transactions 7 jours
        query_7d = """
        SELECT COUNT(*) as count, 
               COALESCE(AVG(price_per_sqft), 0) as avg_price,
               COALESCE(SUM(price_aed), 0) as volume,
               PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_per_sqft) as median_price
        FROM transactions
        WHERE transaction_date >= %s - INTERVAL '7 days'
            AND transaction_date <= %s
        """
        data_7d = db.execute_query(query_7d, (target_date, target_date))
        
        # Transactions 30 jours
        query_30d = """
        SELECT COUNT(*) as count, 
               COALESCE(AVG(price_per_sqft), 0) as avg_price,
               COALESCE(SUM(price_aed), 0) as volume,
               PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_per_sqft) as median_price
        FROM transactions
        WHERE transaction_date >= %s - INTERVAL '30 days'
            AND transaction_date <= %s
        """
        data_30d = db.execute_query(query_30d, (target_date, target_date))
        
        # Période précédente pour variation
        query_prev_7d = """
        SELECT COUNT(*) as count
        FROM transactions
        WHERE transaction_date >= %s - INTERVAL '14 days'
            AND transaction_date < %s - INTERVAL '7 days'
        """
        prev_7d = db.execute_query(query_prev_7d, (target_date, target_date))
        
        # Opportunités
        query_opp = """
        SELECT COUNT(*) as count, AVG(global_score) as avg_score
        FROM opportunities
        WHERE detection_date >= %s - INTERVAL '7 days' AND status = 'active'
        """
        opp_data = db.execute_query(query_opp, (target_date,))
        
        # Calcul variation
        tx_7d = data_7d[0]['count'] if data_7d else 0
        tx_prev_7d = prev_7d[0]['count'] if prev_7d else 0
        variation_pct = ((tx_7d - tx_prev_7d) / tx_prev_7d * 100) if tx_prev_7d > 0 else 0
        
        return {
            'transactions_today': today_data[0]['count'] if today_data else 0,
            'transactions_7d': tx_7d,
            'transactions_30d': data_30d[0]['count'] if data_30d else 0,
            'volume_today': today_data[0]['volume'] if today_data else 0,
            'volume_7d': data_7d[0]['volume'] if data_7d else 0,
            'volume_30d': data_30d[0]['volume'] if data_30d else 0,
            'avg_price_sqft': data_30d[0]['avg_price'] if data_30d else 0,
            'median_price_sqft': data_30d[0]['median_price'] if data_30d else 0,
            'variation_7d_pct': variation_pct,
            'opportunities_count': opp_data[0]['count'] if opp_data else 0,
            'avg_opportunity_score': opp_data[0]['avg_score'] if opp_data else 0,
            # Legacy compatibility
            'transactions_count': data_30d[0]['count'] if data_30d else 0
        }
    
    @staticmethod
    def _get_transaction_stats(target_date: date) -> Dict:
        """Statistiques détaillées des transactions"""
        query = """
        WITH daily_stats AS (
            SELECT 
                transaction_date,
                COUNT(*) as tx_count,
                AVG(price_per_sqft) as avg_price,
                SUM(price_aed) as volume
            FROM transactions
            WHERE transaction_date >= %s - INTERVAL '30 days'
                AND transaction_date <= %s
            GROUP BY transaction_date
            ORDER BY transaction_date
        )
        SELECT 
            transaction_date as date,
            tx_count,
            avg_price,
            volume
        FROM daily_stats
        """
        daily_data = db.execute_query(query, (target_date, target_date))
        
        return {
            'daily_transactions': daily_data or [],
            'total_days': len(daily_data) if daily_data else 0
        }
    
    @staticmethod
    def _get_top_neighborhoods(target_date: date, limit: int = 10) -> List[Dict]:
        """Top quartiers par volume de transactions"""
        query = """
        SELECT 
            community,
            COUNT(*) as transaction_count,
            AVG(price_per_sqft) as avg_price_sqft,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price_per_sqft) as median_price_sqft,
            SUM(price_aed) as total_volume,
            AVG(area_sqft) as avg_area
        FROM transactions
        WHERE transaction_date >= %s - INTERVAL '30 days'
            AND transaction_date <= %s
            AND community IS NOT NULL
        GROUP BY community
        HAVING COUNT(*) >= 2
        ORDER BY transaction_count DESC
        LIMIT %s
        """
        return db.execute_query(query, (target_date, target_date, limit)) or []
    
    @staticmethod
    def _get_property_types_breakdown(target_date: date) -> Dict:
        """Répartition par type de propriété (rooms_bucket)"""
        # Par rooms_bucket (Studio, 1BR, 2BR, 3BR+)
        query_rooms = """
        SELECT 
            COALESCE(rooms_bucket, 'Unknown') as rooms_bucket,
            COUNT(*) as count,
            AVG(price_per_sqft) as avg_price_sqft,
            AVG(price_aed) as avg_price,
            SUM(price_aed) as total_volume
        FROM transactions
        WHERE transaction_date >= %s - INTERVAL '30 days'
            AND transaction_date <= %s
        GROUP BY rooms_bucket
        ORDER BY count DESC
        """
        rooms_data = db.execute_query(query_rooms, (target_date, target_date)) or []
        
        # Par property_type (apartment, villa, townhouse)
        query_types = """
        SELECT 
            COALESCE(property_type, 'other') as property_type,
            COUNT(*) as count,
            AVG(price_per_sqft) as avg_price_sqft,
            AVG(price_aed) as avg_price
        FROM transactions
        WHERE transaction_date >= %s - INTERVAL '30 days'
            AND transaction_date <= %s
        GROUP BY property_type
        ORDER BY count DESC
        """
        types_data = db.execute_query(query_types, (target_date, target_date)) or []
        
        # Offplan vs Ready
        query_offplan = """
        SELECT 
            is_offplan,
            COUNT(*) as count,
            AVG(price_per_sqft) as avg_price_sqft
        FROM transactions
        WHERE transaction_date >= %s - INTERVAL '30 days'
            AND transaction_date <= %s
        GROUP BY is_offplan
        """
        offplan_data = db.execute_query(query_offplan, (target_date, target_date)) or []
        
        return {
            'by_rooms': rooms_data,
            'by_type': types_data,
            'by_offplan': offplan_data
        }
    
    @staticmethod
    def _get_top_opportunities(target_date: date, limit: int = 10) -> list:
        """Top opportunités"""
        query = """
        SELECT * FROM opportunities
        WHERE detection_date = %s AND status = 'active'
        ORDER BY global_score DESC
        LIMIT %s
        """
        return db.execute_query(query, (target_date, limit))
    
    @staticmethod
    def _get_regimes(target_date: date) -> list:
        """Régimes de marché"""
        query = """
        SELECT * FROM market_regimes
        WHERE regime_date = %s
        ORDER BY confidence_score DESC
        LIMIT 20
        """
        return db.execute_query(query, (target_date,))
    
    @staticmethod
    def _get_daily_brief(target_date: date) -> Dict:
        """Brief quotidien CIO"""
        query = """
        SELECT * FROM daily_briefs
        WHERE brief_date = %s
        """
        results = db.execute_query(query, (target_date,))
        return results[0] if results else None
