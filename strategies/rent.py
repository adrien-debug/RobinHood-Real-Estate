"""
Stratégie RENT - Cashflow locatif
"""
from typing import Dict
from decimal import Decimal
from strategies.base import BaseStrategy


class RentStrategy(BaseStrategy):
    """
    Stratégie RENT (cashflow locatif)
    
    Poids forts :
    - Rendement locatif élevé
    - Tension locative (demande > offre)
    - Stabilité des prix
    - Régime DISTRIBUTION ou EXPANSION
    
    Pénalités :
    - Volatilité élevée
    - Risque réglementaire (plafonnement loyers)
    """
    
    def __init__(self):
        super().__init__("RENT")
    
    def score(self, opportunity: Dict, context: Dict) -> float:
        """Calculer le score RENT"""
        
        # 1. Rendement estimé (35% du score)
        # Note : nécessite rental_index pour calcul précis
        # Ici on utilise une estimation basée sur le discount
        discount_pct = opportunity.get('discount_pct', 0)
        price_per_sqft = opportunity.get('price_per_sqft', 0)
        
        # Rendement estimé : loyer annuel / prix d'achat
        # Approximation : 5-8% rendement typique à Dubaï
        estimated_yield = self._estimate_rental_yield(price_per_sqft, discount_pct)
        yield_score = self._get_yield_score(estimated_yield) * 0.35
        
        # 2. Stabilité prix (25% du score)
        baseline = context.get('baseline', {})
        volatility = baseline.get('volatility', 0.15)
        stability_score = self._get_stability_score(volatility) * 0.25
        
        # 3. Liquidité (20% du score)
        transaction_count = baseline.get('transaction_count', 0)
        liquidity_score = self._get_liquidity_score(transaction_count) * 0.20
        
        # 4. Régime de marché (20% du score)
        regime = context.get('regime', 'NEUTRAL')
        regime_score = self._get_regime_score(regime, 'rent') * 0.20
        
        raw_score = yield_score + stability_score + liquidity_score + regime_score
        
        # Pénalités
        penalties = 0
        
        # Volatilité excessive
        if volatility and volatility > 0.25:
            penalties += 15
        
        final_score = raw_score - penalties
        
        return self._normalize_score(final_score)
    
    def _estimate_rental_yield(self, price_per_sqft: Decimal, discount_pct: Decimal) -> float:
        """
        Estimer le rendement locatif
        
        Approximation basée sur :
        - Prix d'achat (avec discount)
        - Loyer moyen estimé pour Dubaï
        """
        if not price_per_sqft or price_per_sqft <= 0:
            return 5.0  # Défaut
        
        # Loyer annuel estimé par sqft (AED)
        # Approximation : 80-120 AED/sqft/an selon zone
        estimated_rent_per_sqft = 100.0
        
        # Rendement = (loyer annuel / prix achat) * 100
        # Avec discount, le rendement augmente
        base_yield = (estimated_rent_per_sqft / float(price_per_sqft)) * 100
        
        # Bonus discount
        discount_bonus = float(discount_pct) * 0.05  # 10% discount = +0.5% yield
        
        return base_yield + discount_bonus
    
    def _get_yield_score(self, yield_pct: float) -> float:
        """Score basé sur le rendement locatif"""
        # 4% = 40 points
        # 6% = 70 points
        # 8%+ = 100 points
        if yield_pct >= 8.0:
            return 100.0
        elif yield_pct >= 6.0:
            return 70.0 + (yield_pct - 6.0) * 15.0
        elif yield_pct >= 4.0:
            return 40.0 + (yield_pct - 4.0) * 15.0
        else:
            return yield_pct * 10.0
    
    def _get_stability_score(self, volatility: Decimal) -> float:
        """Score basé sur la stabilité (inverse de la volatilité)"""
        if volatility is None:
            return 50.0
        
        vol_float = float(volatility)
        
        # Faible volatilité = bon pour location
        if vol_float < 0.05:
            return 100.0
        elif vol_float < 0.10:
            return 80.0
        elif vol_float < 0.15:
            return 60.0
        elif vol_float < 0.20:
            return 40.0
        else:
            return 20.0
