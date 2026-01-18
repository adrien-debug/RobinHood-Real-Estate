"""
Stratégie FLIP - Achat-revente rapide

Enrichi avec KPIs avancés :
- LAD (Liquidity-Adjusted Discount) : remplace le discount simple
- TLS (Transaction-to-Listing Spread) : détecte les opportunités de marge
- ORD (Offplan Risk Delta) : évalue le risque offplan pour flip
"""
from typing import Dict
from strategies.base import BaseStrategy


class FlipStrategy(BaseStrategy):
    """
    Stratégie FLIP (achat-revente rapide)
    
    Poids forts :
    - Sous-valorisation importante (LAD)
    - Liquidité élevée (facilité de revente)
    - Momentum court terme positif
    - Régime EXPANSION ou ACCUMULATION
    - Spread listing/transaction favorable (TLS)
    
    Pénalités :
    - Supply future élevée
    - Régime RETOURNEMENT
    - Offplan premium élevé (ORD > 0.15)
    """
    
    def __init__(self):
        super().__init__("FLIP")
    
    def score(self, opportunity: Dict, context: Dict) -> float:
        """Calculer le score FLIP enrichi avec KPIs avancés"""
        
        # Récupérer le contexte KPI
        kpi_ctx = self._get_kpi_context(
            opportunity.get('community', ''),
            opportunity.get('rooms_bucket')
        )
        
        # 1. Discount ajusté (35% du score)
        # Utilise LAD si disponible, sinon discount classique
        discount_pct = opportunity.get('discount_pct', 0)
        if kpi_ctx.lad is not None and kpi_ctx.lad > 0:
            # LAD intègre déjà la liquidité, score plus agressif
            lad_score = min(100, kpi_ctx.lad * 20)  # LAD de 5 = 100 points
            discount_score = lad_score * 0.35
        else:
            discount_score = self._get_discount_score(discount_pct) * 0.35
        
        # 2. Liquidité (25% du score)
        baseline = context.get('baseline', {})
        transaction_count = baseline.get('transaction_count', 0)
        liquidity_score = self._get_liquidity_score(transaction_count) * 0.25
        
        # 3. Spread TLS (15% du score) - nouveau
        # TLS > 0 = listings plus chers que transactions = marge de revente
        tls_score = 0
        if kpi_ctx.tls is not None:
            if kpi_ctx.tls > 0.15:
                tls_score = 100 * 0.15  # Excellent spread
            elif kpi_ctx.tls > 0.10:
                tls_score = 80 * 0.15
            elif kpi_ctx.tls > 0.05:
                tls_score = 60 * 0.15
            elif kpi_ctx.tls > 0:
                tls_score = 40 * 0.15
            else:
                tls_score = 20 * 0.15  # Listings moins chers = risque
        else:
            tls_score = 50 * 0.15  # Neutre si pas de données
        
        # 4. Momentum (10% du score)
        momentum = baseline.get('momentum')
        momentum_score = self._get_momentum_score(momentum) * 0.10
        
        # 5. Régime de marché (15% du score)
        regime = context.get('regime', 'NEUTRAL')
        regime_score = self._get_regime_score(regime, 'flip') * 0.15
        
        # Score brut
        raw_score = discount_score + liquidity_score + tls_score + momentum_score + regime_score
        
        # Pénalités
        penalties = 0
        
        # Pénalité supply risk (utilise le risque du contexte KPI si disponible)
        supply_risk = kpi_ctx.supply_risk if kpi_ctx.supply_risk != "UNKNOWN" else context.get('supply_risk', 'low')
        if supply_risk == 'HIGH':
            penalties += 20
        elif supply_risk == 'MEDIUM':
            penalties += 10
        
        # Pénalité régime RETOURNEMENT
        if regime == 'RETOURNEMENT':
            penalties += 15
        
        # Pénalité ORD élevé (offplan premium trop important = risque)
        if kpi_ctx.ord is not None and kpi_ctx.ord > 0.15:
            penalties += 10  # Offplan surpayé de 15%+ = risque de correction
        
        final_score = raw_score - penalties
        
        return self._normalize_score(final_score)
