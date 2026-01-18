"""
Classe de base pour les stratégies de scoring

Enrichi avec les KPIs avancés :
- TLS (Transaction-to-Listing Spread)
- LAD (Liquidity-Adjusted Discount)
- RSG (Rental Stress Gap)
- SPI (Supply Pressure Index)
- GPI (Geo-Premium Index)
- RCWM (Regime Confidence-Weighted Momentum)
- ORD (Offplan Risk Delta)
- APS (Anomaly Persistence Score)
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from decimal import Decimal
from loguru import logger

from core.db import db
from core.models import KPIContext


class BaseStrategy(ABC):
    """Stratégie de base abstraite"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def score(self, opportunity: Dict, context: Dict) -> float:
        """
        Calculer le score pour une opportunité
        
        Args:
            opportunity: Données de l'opportunité (anomalie détectée)
            context: Contexte marché (baseline, régime, kpis, etc.)
        
        Returns:
            Score entre 0 et 100
        """
        pass
    
    def _normalize_score(self, raw_score: float) -> float:
        """Normaliser un score entre 0 et 100"""
        return max(0.0, min(100.0, raw_score))
    
    def _get_kpi_context(
        self, 
        community: str, 
        rooms_bucket: Optional[str] = None,
        window_days: int = 30
    ) -> KPIContext:
        """
        Récupérer le contexte KPI pour le scoring enrichi
        
        Args:
            community: Communauté
            rooms_bucket: Type de chambres (optionnel)
            window_days: Fenêtre en jours
            
        Returns:
            KPIContext avec les KPIs et risques
        """
        kpi_context = KPIContext()
        
        # Récupérer les KPIs
        kpi_query = """
        SELECT tls, lad, rsg, spi, gpi, rcwm, ord, aps
        FROM kpis
        WHERE community = %s
            AND window_days = %s
        """
        params = [community, window_days]
        
        if rooms_bucket:
            kpi_query += " AND rooms_bucket = %s"
            params.append(rooms_bucket)
        
        kpi_query += " ORDER BY calculation_date DESC LIMIT 1"
        
        try:
            results = db.execute_query(kpi_query, tuple(params))
            if results:
                row = results[0]
                kpi_context.tls = float(row["tls"]) if row.get("tls") else None
                kpi_context.lad = float(row["lad"]) if row.get("lad") else None
                kpi_context.rsg = float(row["rsg"]) if row.get("rsg") else None
                kpi_context.spi = float(row["spi"]) if row.get("spi") else None
                kpi_context.gpi = float(row["gpi"]) if row.get("gpi") else None
                kpi_context.rcwm = float(row["rcwm"]) if row.get("rcwm") else None
                kpi_context.ord = float(row["ord"]) if row.get("ord") else None
                kpi_context.aps = float(row["aps"]) if row.get("aps") else None
        except Exception as e:
            logger.warning(f"Erreur récupération KPIs pour scoring : {e}")
        
        # Récupérer les risques
        risk_query = """
        SELECT 
            supply_risk_level,
            volatility_risk_level,
            divergence_risk_level,
            overall_risk_score
        FROM risk_summaries
        WHERE community = %s
        ORDER BY summary_date DESC
        LIMIT 1
        """
        
        try:
            risk_results = db.execute_query(risk_query, (community,))
            if risk_results:
                row = risk_results[0]
                kpi_context.supply_risk = row.get("supply_risk_level", "UNKNOWN")
                kpi_context.volatility_risk = row.get("volatility_risk_level", "UNKNOWN")
                kpi_context.divergence_risk = row.get("divergence_risk_level", "UNKNOWN")
                kpi_context.overall_risk_score = float(row["overall_risk_score"]) if row.get("overall_risk_score") else None
        except Exception as e:
            logger.warning(f"Erreur récupération risques pour scoring : {e}")
        
        return kpi_context
    
    def _get_discount_score(self, discount_pct: Decimal) -> float:
        """Score basé sur le discount (0-100)"""
        # 10% discount = 50 points
        # 20% discount = 75 points
        # 30%+ discount = 100 points
        if discount_pct >= 30:
            return 100.0
        elif discount_pct >= 20:
            return 75.0 + (discount_pct - 20) * 2.5
        elif discount_pct >= 10:
            return 50.0 + (discount_pct - 10) * 2.5
        else:
            return discount_pct * 5.0
    
    def _get_liquidity_score(self, transaction_count: int) -> float:
        """Score de liquidité basé sur le volume de transactions"""
        # 5 tx = 25 points
        # 10 tx = 50 points
        # 20+ tx = 100 points
        if transaction_count >= 20:
            return 100.0
        elif transaction_count >= 10:
            return 50.0 + (transaction_count - 10) * 5.0
        elif transaction_count >= 5:
            return 25.0 + (transaction_count - 5) * 5.0
        else:
            return transaction_count * 5.0
    
    def _get_momentum_score(self, momentum: Decimal) -> float:
        """Score basé sur le momentum (variation de prix)"""
        # momentum > 0 = prix en hausse (bon pour long term, neutre pour flip)
        # momentum < 0 = prix en baisse (risque)
        if momentum is None:
            return 50.0
        
        momentum_float = float(momentum)
        
        if momentum_float > 0.10:  # +10%
            return 100.0
        elif momentum_float > 0.05:  # +5%
            return 75.0
        elif momentum_float > 0:
            return 50.0 + momentum_float * 500
        elif momentum_float > -0.05:
            return 50.0 + momentum_float * 500
        else:
            return 0.0
    
    def _get_regime_score(self, regime: str, strategy_type: str) -> float:
        """
        Score basé sur le régime de marché et la stratégie
        
        Args:
            regime: ACCUMULATION, EXPANSION, DISTRIBUTION, RETOURNEMENT, NEUTRAL
            strategy_type: flip, rent, long_term
        """
        regime_scores = {
            'flip': {
                'ACCUMULATION': 80.0,  # Bon timing pour flip
                'EXPANSION': 90.0,     # Excellent pour flip
                'DISTRIBUTION': 50.0,  # Risqué
                'RETOURNEMENT': 20.0,  # Très risqué
                'NEUTRAL': 60.0
            },
            'rent': {
                'ACCUMULATION': 70.0,
                'EXPANSION': 75.0,
                'DISTRIBUTION': 80.0,  # Bon pour location (marché stable)
                'RETOURNEMENT': 60.0,
                'NEUTRAL': 70.0
            },
            'long_term': {
                'ACCUMULATION': 100.0,  # Meilleur moment pour long term
                'EXPANSION': 80.0,
                'DISTRIBUTION': 40.0,
                'RETOURNEMENT': 20.0,
                'NEUTRAL': 60.0
            }
        }
        
        return regime_scores.get(strategy_type, {}).get(regime, 50.0)
