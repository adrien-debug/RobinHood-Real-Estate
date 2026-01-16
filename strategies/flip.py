"""
Stratégie FLIP - Achat-revente rapide
"""
from typing import Dict
from strategies.base import BaseStrategy


class FlipStrategy(BaseStrategy):
    """
    Stratégie FLIP (achat-revente rapide)
    
    Poids forts :
    - Sous-valorisation importante
    - Liquidité élevée (facilité de revente)
    - Momentum court terme positif
    - Régime EXPANSION ou ACCUMULATION
    
    Pénalités :
    - Supply future élevée
    - Régime RETOURNEMENT
    """
    
    def __init__(self):
        super().__init__("FLIP")
    
    def score(self, opportunity: Dict, context: Dict) -> float:
        """Calculer le score FLIP"""
        
        # 1. Discount (40% du score)
        discount_pct = opportunity.get('discount_pct', 0)
        discount_score = self._get_discount_score(discount_pct) * 0.40
        
        # 2. Liquidité (30% du score)
        baseline = context.get('baseline', {})
        transaction_count = baseline.get('transaction_count', 0)
        liquidity_score = self._get_liquidity_score(transaction_count) * 0.30
        
        # 3. Momentum (15% du score)
        momentum = baseline.get('momentum')
        momentum_score = self._get_momentum_score(momentum) * 0.15
        
        # 4. Régime de marché (15% du score)
        regime = context.get('regime', 'NEUTRAL')
        regime_score = self._get_regime_score(regime, 'flip') * 0.15
        
        # Score brut
        raw_score = discount_score + liquidity_score + momentum_score + regime_score
        
        # Pénalités
        penalties = 0
        
        # Pénalité supply risk
        supply_risk = context.get('supply_risk', 'low')
        if supply_risk == 'high':
            penalties += 20
        elif supply_risk == 'medium':
            penalties += 10
        
        # Pénalité régime RETOURNEMENT
        if regime == 'RETOURNEMENT':
            penalties += 15
        
        final_score = raw_score - penalties
        
        return self._normalize_score(final_score)
