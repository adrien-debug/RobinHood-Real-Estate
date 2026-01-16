"""
Classe de base pour les stratégies de scoring
"""
from abc import ABC, abstractmethod
from typing import Dict
from decimal import Decimal


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
            context: Contexte marché (baseline, régime, etc.)
        
        Returns:
            Score entre 0 et 100
        """
        pass
    
    def _normalize_score(self, raw_score: float) -> float:
        """Normaliser un score entre 0 et 100"""
        return max(0.0, min(100.0, raw_score))
    
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
