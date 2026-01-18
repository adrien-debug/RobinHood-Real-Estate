"""
Stratégie RENT - Cashflow locatif

Enrichi avec KPIs avancés :
- RSG (Rental Stress Gap) : détecte les zones en tension locative
- GPI (Geo-Premium Index) : valorise les emplacements premium
"""
from typing import Dict
from decimal import Decimal
from strategies.base import BaseStrategy


class RentStrategy(BaseStrategy):
    """
    Stratégie RENT (cashflow locatif)
    
    Poids forts :
    - Rendement locatif élevé (avec RSG)
    - Tension locative positive (RSG > 0)
    - Stabilité des prix
    - Localisation premium (GPI)
    - Régime DISTRIBUTION ou EXPANSION
    
    Pénalités :
    - Volatilité élevée
    - RSG très négatif (offre > demande)
    """
    
    def __init__(self):
        super().__init__("RENT")
    
    def score(self, opportunity: Dict, context: Dict) -> float:
        """Calculer le score RENT enrichi avec KPIs avancés"""
        
        # Récupérer le contexte KPI
        kpi_ctx = self._get_kpi_context(
            opportunity.get('community', ''),
            opportunity.get('rooms_bucket')
        )
        
        # 1. Rendement avec RSG (35% du score)
        discount_pct = opportunity.get('discount_pct', 0)
        price_per_sqft = opportunity.get('price_per_sqft', 0)
        
        # Utilise RSG pour ajuster le score de rendement
        base_yield = self._estimate_rental_yield(price_per_sqft, discount_pct)
        
        if kpi_ctx.rsg is not None:
            # RSG > 0 = loyers au-dessus des attentes = tension locative
            # RSG < 0 = loyers sous les attentes = offre excédentaire
            if kpi_ctx.rsg > 0.15:
                yield_bonus = 20  # Forte tension locative
            elif kpi_ctx.rsg > 0.05:
                yield_bonus = 10
            elif kpi_ctx.rsg > -0.05:
                yield_bonus = 0  # Équilibré
            elif kpi_ctx.rsg > -0.15:
                yield_bonus = -10
            else:
                yield_bonus = -20  # Offre excédentaire
            
            adjusted_yield = base_yield + (yield_bonus * 0.1)  # Ajustement modéré
        else:
            adjusted_yield = base_yield
        
        yield_score = self._get_yield_score(adjusted_yield) * 0.35
        
        # 2. Stabilité prix (20% du score)
        baseline = context.get('baseline', {})
        volatility = baseline.get('volatility', 0.15)
        stability_score = self._get_stability_score(volatility) * 0.20
        
        # 3. Score de localisation GPI (20% du score) - nouveau
        gpi_score = 0
        if kpi_ctx.gpi is not None:
            # GPI basé sur location_score * (1 + price_premium)
            if kpi_ctx.gpi >= 80:
                gpi_score = 100 * 0.20
            elif kpi_ctx.gpi >= 60:
                gpi_score = 75 * 0.20
            elif kpi_ctx.gpi >= 40:
                gpi_score = 50 * 0.20
            else:
                gpi_score = 25 * 0.20
        else:
            gpi_score = 50 * 0.20  # Neutre
        
        # 4. Liquidité (10% du score)
        transaction_count = baseline.get('transaction_count', 0)
        liquidity_score = self._get_liquidity_score(transaction_count) * 0.10
        
        # 5. Régime de marché (15% du score)
        regime = context.get('regime', 'NEUTRAL')
        regime_score = self._get_regime_score(regime, 'rent') * 0.15
        
        raw_score = yield_score + stability_score + gpi_score + liquidity_score + regime_score
        
        # Pénalités
        penalties = 0
        
        # Volatilité excessive (utilise le risque si disponible)
        volatility_risk = kpi_ctx.volatility_risk
        if volatility_risk == "HIGH":
            penalties += 15
        elif volatility_risk == "MEDIUM":
            penalties += 5
        elif volatility and float(volatility) > 0.25:
            penalties += 15
        
        # RSG très négatif = marché locatif saturé
        if kpi_ctx.rsg is not None and kpi_ctx.rsg < -0.20:
            penalties += 10
        
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
            return max(0, yield_pct * 10.0)
    
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
