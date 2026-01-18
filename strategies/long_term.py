"""
Stratégie LONG_TERM - Appréciation du capital

Enrichi avec KPIs avancés :
- SPI (Supply Pressure Index) : évalue précisément la pression de supply
- RCWM (Regime Confidence-Weighted Momentum) : momentum pondéré par confiance
- APS (Anomaly Persistence Score) : détecte les anomalies persistantes
"""
from typing import Dict
from strategies.base import BaseStrategy


class LongTermStrategy(BaseStrategy):
    """
    Stratégie LONG_TERM (appréciation du capital)
    
    Poids forts :
    - Zone en ACCUMULATION ou EXPANSION
    - Faible supply future (SPI bas)
    - Momentum positif pondéré (RCWM)
    - Discount important (point d'entrée bas)
    - Anomalies persistantes (APS) suggèrent sous-évaluation
    
    Pénalités :
    - Volatilité excessive
    - SPI élevé (supply future importante)
    - Régime RETOURNEMENT
    """
    
    def __init__(self):
        super().__init__("LONG_TERM")
    
    def score(self, opportunity: Dict, context: Dict) -> float:
        """Calculer le score LONG_TERM enrichi avec KPIs avancés"""
        
        # Récupérer le contexte KPI
        kpi_ctx = self._get_kpi_context(
            opportunity.get('community', ''),
            opportunity.get('rooms_bucket')
        )
        
        # 1. Régime de marché avec RCWM (30% du score)
        regime = context.get('regime', 'NEUTRAL')
        base_regime_score = self._get_regime_score(regime, 'long_term')
        
        # Ajuster avec RCWM si disponible
        if kpi_ctx.rcwm is not None:
            # RCWM = momentum * confidence
            # RCWM > 0.05 = signal fort positif
            # RCWM < -0.05 = signal fort négatif
            if kpi_ctx.rcwm > 0.05:
                rcwm_bonus = 15
            elif kpi_ctx.rcwm > 0.02:
                rcwm_bonus = 8
            elif kpi_ctx.rcwm > 0:
                rcwm_bonus = 3
            elif kpi_ctx.rcwm > -0.02:
                rcwm_bonus = 0
            elif kpi_ctx.rcwm > -0.05:
                rcwm_bonus = -8
            else:
                rcwm_bonus = -15
            
            regime_score = min(100, max(0, base_regime_score + rcwm_bonus)) * 0.30
        else:
            regime_score = base_regime_score * 0.30
        
        # 2. Discount (25% du score)
        discount_pct = opportunity.get('discount_pct', 0)
        discount_score = self._get_discount_score(discount_pct) * 0.25
        
        # 3. Supply avec SPI (20% du score) - nouveau
        if kpi_ctx.spi is not None:
            # SPI normalisé 0-100, plus bas = moins de supply = mieux
            spi_score = (100 - kpi_ctx.spi) * 0.20
        else:
            supply_risk = context.get('supply_risk', 'low')
            spi_score = self._get_supply_score(supply_risk) * 0.20
        
        # 4. Momentum classique (15% du score)
        baseline = context.get('baseline', {})
        momentum = baseline.get('momentum')
        momentum_score = self._get_momentum_score(momentum) * 0.15
        
        # 5. Anomaly Persistence (10% du score) - nouveau
        # APS élevé = anomalie persistante = possibilité de sous-évaluation structurelle
        aps_score = 0
        if kpi_ctx.aps is not None:
            # APS = jours d'anomalie / fenêtre
            if kpi_ctx.aps > 0.7:
                aps_score = 100 * 0.10  # Anomalie très persistante
            elif kpi_ctx.aps > 0.5:
                aps_score = 75 * 0.10
            elif kpi_ctx.aps > 0.3:
                aps_score = 50 * 0.10
            elif kpi_ctx.aps > 0.1:
                aps_score = 30 * 0.10
            else:
                aps_score = 10 * 0.10  # Peu d'anomalies
        else:
            aps_score = 30 * 0.10  # Neutre
        
        raw_score = regime_score + discount_score + spi_score + momentum_score + aps_score
        
        # Pénalités
        penalties = 0
        
        # Volatilité excessive
        volatility_risk = kpi_ctx.volatility_risk
        if volatility_risk == "HIGH":
            penalties += 20
        elif volatility_risk == "MEDIUM":
            penalties += 10
        else:
            volatility = baseline.get('volatility', 0.15)
            if volatility and float(volatility) > 0.25:
                penalties += 20
            elif volatility and float(volatility) > 0.20:
                penalties += 10
        
        # Régime RETOURNEMENT
        if regime == 'RETOURNEMENT':
            penalties += 25
        
        # SPI très élevé (supply massive)
        if kpi_ctx.spi is not None and kpi_ctx.spi > 80:
            penalties += 15
        elif kpi_ctx.supply_risk == "HIGH":
            penalties += 15
        
        final_score = raw_score - penalties
        
        return self._normalize_score(final_score)
    
    def _get_supply_score(self, supply_risk: str) -> float:
        """Score basé sur le risque de supply future"""
        supply_scores = {
            'low': 100.0,
            'LOW': 100.0,
            'medium': 60.0,
            'MEDIUM': 60.0,
            'high': 20.0,
            'HIGH': 20.0,
            'unknown': 50.0,
            'UNKNOWN': 50.0
        }
        return supply_scores.get(supply_risk, 50.0)
