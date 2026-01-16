"""
Stratégie LONG_TERM - Appréciation du capital
"""
from typing import Dict
from strategies.base import BaseStrategy


class LongTermStrategy(BaseStrategy):
    """
    Stratégie LONG_TERM (appréciation du capital)
    
    Poids forts :
    - Zone en ACCUMULATION ou EXPANSION
    - Faible supply future
    - Momentum positif long terme
    - Discount important (point d'entrée bas)
    
    Pénalités :
    - Volatilité excessive
    - Supply future élevée
    - Régime RETOURNEMENT
    """
    
    def __init__(self):
        super().__init__("LONG_TERM")
    
    def score(self, opportunity: Dict, context: Dict) -> float:
        """Calculer le score LONG_TERM"""
        
        # 1. Régime de marché (35% du score)
        # ACCUMULATION = meilleur moment pour long term
        regime = context.get('regime', 'NEUTRAL')
        regime_score = self._get_regime_score(regime, 'long_term') * 0.35
        
        # 2. Discount (30% du score)
        # Point d'entrée bas = meilleur potentiel d'appréciation
        discount_pct = opportunity.get('discount_pct', 0)
        discount_score = self._get_discount_score(discount_pct) * 0.30
        
        # 3. Momentum long terme (20% du score)
        baseline = context.get('baseline', {})
        momentum = baseline.get('momentum')
        momentum_score = self._get_momentum_score(momentum) * 0.20
        
        # 4. Supply risk (15% du score)
        # Faible supply future = meilleur potentiel d'appréciation
        supply_risk = context.get('supply_risk', 'low')
        supply_score = self._get_supply_score(supply_risk) * 0.15
        
        raw_score = regime_score + discount_score + momentum_score + supply_score
        
        # Pénalités
        penalties = 0
        
        # Volatilité excessive
        volatility = baseline.get('volatility', 0.15)
        if volatility and volatility > 0.25:
            penalties += 20
        elif volatility and volatility > 0.20:
            penalties += 10
        
        # Régime RETOURNEMENT
        if regime == 'RETOURNEMENT':
            penalties += 25
        
        # Supply future élevée
        if supply_risk == 'high':
            penalties += 15
        
        final_score = raw_score - penalties
        
        return self._normalize_score(final_score)
    
    def _get_supply_score(self, supply_risk: str) -> float:
        """Score basé sur le risque de supply future"""
        supply_scores = {
            'low': 100.0,
            'medium': 60.0,
            'high': 20.0,
            'unknown': 50.0
        }
        return supply_scores.get(supply_risk, 50.0)
