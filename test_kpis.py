"""
Tests pour les KPIs avancés et le pipeline de données

Tests unitaires :
- Formules de calcul des 8 KPIs
- Filtrage des outliers
- Classification des risques

Tests d'intégration :
- Pipeline complet compute_features
- Pipeline compute_kpis
- Pipeline compute_risk_summary
"""
import unittest
from datetime import date, timedelta
from decimal import Decimal
import math

# Import des modules à tester
from pipelines.compute_kpis import (
    _calc_tls,
    _calc_lad,
    _calc_rsg,
    _calc_spi,
    _calc_gpi,
    _calc_rcwm,
    _calc_ord,
    _calc_aps
)
from pipelines.compute_risk_summary import (
    _classify_risk,
    _compute_overall_risk_score,
    SUPPLY_THRESHOLDS,
    VOLATILITY_THRESHOLDS,
    DIVERGENCE_THRESHOLDS
)
from pipelines.compute_features import (
    MIN_PRICE_PER_SQFT,
    MAX_PRICE_PER_SQFT
)
from core.models import Feature, KPI, RiskSummary, QualityLog


class TestKPIFormulas(unittest.TestCase):
    """Tests unitaires des formules de KPIs"""
    
    def test_tls_positive_spread(self):
        """TLS avec listings plus chers que transactions"""
        # Listings à 1200, Transactions à 1000 -> spread de 20%
        result = _calc_tls(Decimal("1000"), Decimal("1200"))
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 0.20, places=4)
    
    def test_tls_negative_spread(self):
        """TLS avec listings moins chers que transactions"""
        # Listings à 900, Transactions à 1000 -> spread de -10%
        result = _calc_tls(Decimal("1000"), Decimal("900"))
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, -0.10, places=4)
    
    def test_tls_zero_tx(self):
        """TLS avec transactions à zéro"""
        result = _calc_tls(Decimal("0"), Decimal("1200"))
        self.assertIsNone(result)
    
    def test_tls_none_values(self):
        """TLS avec valeurs None"""
        result = _calc_tls(None, Decimal("1200"))
        self.assertIsNone(result)
    
    def test_lad_calculation(self):
        """LAD = discount * log(1 + tx_count)"""
        # Discount 10%, 20 transactions
        result = _calc_lad(10.0, 20)
        expected = 10.0 * math.log(21)  # log(1 + 20)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, expected, places=4)
    
    def test_lad_zero_transactions(self):
        """LAD avec zéro transactions"""
        result = _calc_lad(10.0, 0)
        # log(1) = 0, donc LAD = 0
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 0.0, places=4)
    
    def test_rsg_positive_gap(self):
        """RSG avec loyers au-dessus des attentes"""
        # Loyer médian 100k, prix/sqft 1000, avg sqft 1000, yield 6%
        # Expected rent = 1000 * 1000 * 0.06 = 60000
        # RSG = (100000 - 60000) / 60000 = 0.667
        result = _calc_rsg(
            Decimal("100000"),
            Decimal("1000"),
            Decimal("1000")
        )
        self.assertIsNotNone(result)
        self.assertGreater(result, 0.5)
    
    def test_rsg_negative_gap(self):
        """RSG avec loyers en dessous des attentes"""
        # Loyer médian 40k, prix/sqft 1000, avg sqft 1000, yield 6%
        # Expected rent = 60000
        # RSG = (40000 - 60000) / 60000 = -0.333
        result = _calc_rsg(
            Decimal("40000"),
            Decimal("1000"),
            Decimal("1000")
        )
        self.assertIsNotNone(result)
        self.assertLess(result, 0)
    
    def test_spi_normalization(self):
        """SPI normalisé entre 0 et 100"""
        # 200 unités planifiées, 100 transactions -> ratio 2 -> SPI = 100
        result = _calc_spi(200, 100)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 100.0, places=1)
        
        # 50 unités planifiées, 100 transactions -> ratio 0.5 -> SPI = 25
        result = _calc_spi(50, 100)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 25.0, places=1)
    
    def test_spi_zero_transactions(self):
        """SPI avec zéro transactions -> valeur neutre"""
        result = _calc_spi(100, 0)
        self.assertIsNotNone(result)
        self.assertEqual(result, 50.0)
    
    def test_gpi_calculation(self):
        """GPI = location_score * (1 + price_premium)"""
        # Score localisation 80, premium 10%
        result = _calc_gpi(80.0, 0.10)
        expected = 80.0 * 1.10
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, expected, places=2)
    
    def test_gpi_no_premium(self):
        """GPI sans premium"""
        result = _calc_gpi(75.0, None)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 75.0, places=2)
    
    def test_rcwm_calculation(self):
        """RCWM = momentum * regime_confidence"""
        # Momentum +5%, confidence 80%
        result = _calc_rcwm(Decimal("0.05"), Decimal("0.80"))
        expected = 0.05 * 0.80
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, expected, places=4)
    
    def test_ord_positive_delta(self):
        """ORD avec offplan plus cher que ready"""
        # Offplan 1100, Ready 1000 -> ORD = 10%
        result = _calc_ord(Decimal("1100"), Decimal("1000"))
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 0.10, places=4)
    
    def test_ord_negative_delta(self):
        """ORD avec offplan moins cher que ready"""
        # Offplan 900, Ready 1000 -> ORD = -10%
        result = _calc_ord(Decimal("900"), Decimal("1000"))
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, -0.10, places=4)
    
    def test_aps_calculation(self):
        """APS = days_active / window_days"""
        # 15 jours actifs sur 30 jours
        result = _calc_aps(15, 30)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result, 0.50, places=2)
    
    def test_aps_zero_window(self):
        """APS avec fenêtre à zéro"""
        result = _calc_aps(10, 0)
        self.assertIsNone(result)


class TestRiskClassification(unittest.TestCase):
    """Tests de classification des risques"""
    
    def test_classify_risk_low(self):
        """Classification risque LOW"""
        # SPI < 30 = LOW
        result = _classify_risk(25.0, SUPPLY_THRESHOLDS)
        self.assertEqual(result, "LOW")
    
    def test_classify_risk_medium(self):
        """Classification risque MEDIUM"""
        # SPI entre 30 et 70 = MEDIUM
        result = _classify_risk(50.0, SUPPLY_THRESHOLDS)
        self.assertEqual(result, "MEDIUM")
    
    def test_classify_risk_high(self):
        """Classification risque HIGH"""
        # SPI > 70 = HIGH
        result = _classify_risk(85.0, SUPPLY_THRESHOLDS)
        self.assertEqual(result, "HIGH")
    
    def test_classify_risk_none(self):
        """Classification avec valeur None"""
        result = _classify_risk(None, SUPPLY_THRESHOLDS)
        self.assertEqual(result, "UNKNOWN")
    
    def test_volatility_thresholds(self):
        """Test des seuils de volatilité"""
        self.assertEqual(_classify_risk(0.10, VOLATILITY_THRESHOLDS), "LOW")
        self.assertEqual(_classify_risk(0.20, VOLATILITY_THRESHOLDS), "MEDIUM")
        self.assertEqual(_classify_risk(0.30, VOLATILITY_THRESHOLDS), "HIGH")
    
    def test_divergence_thresholds(self):
        """Test des seuils de divergence"""
        self.assertEqual(_classify_risk(0.05, DIVERGENCE_THRESHOLDS), "LOW")
        self.assertEqual(_classify_risk(0.15, DIVERGENCE_THRESHOLDS), "MEDIUM")
        self.assertEqual(_classify_risk(0.25, DIVERGENCE_THRESHOLDS), "HIGH")
    
    def test_overall_risk_score(self):
        """Test du score global de risque"""
        # Tous LOW -> score bas
        score_low = _compute_overall_risk_score("LOW", "LOW", "LOW")
        self.assertLess(score_low, 30)
        
        # Tous HIGH -> score élevé
        score_high = _compute_overall_risk_score("HIGH", "HIGH", "HIGH")
        self.assertGreater(score_high, 80)
        
        # Mix -> score intermédiaire
        score_mix = _compute_overall_risk_score("LOW", "MEDIUM", "HIGH")
        self.assertGreater(score_mix, 30)
        self.assertLess(score_mix, 70)


class TestOutlierFiltering(unittest.TestCase):
    """Tests du filtrage des outliers"""
    
    def test_min_threshold(self):
        """Test du seuil minimum (500 AED/sqft)"""
        self.assertEqual(MIN_PRICE_PER_SQFT, 500)
    
    def test_max_threshold(self):
        """Test du seuil maximum (10000 AED/sqft)"""
        self.assertEqual(MAX_PRICE_PER_SQFT, 10000)
    
    def test_valid_price_range(self):
        """Prix valides dans la plage"""
        valid_prices = [600, 1000, 1500, 2000, 5000, 8000, 9500]
        for price in valid_prices:
            is_valid = MIN_PRICE_PER_SQFT <= price <= MAX_PRICE_PER_SQFT
            self.assertTrue(is_valid, f"Prix {price} devrait être valide")
    
    def test_invalid_prices_low(self):
        """Prix invalides (trop bas)"""
        invalid_prices = [100, 200, 400, 499]
        for price in invalid_prices:
            is_valid = MIN_PRICE_PER_SQFT <= price <= MAX_PRICE_PER_SQFT
            self.assertFalse(is_valid, f"Prix {price} devrait être invalide (trop bas)")
    
    def test_invalid_prices_high(self):
        """Prix invalides (trop élevés)"""
        invalid_prices = [10001, 15000, 20000, 50000]
        for price in invalid_prices:
            is_valid = MIN_PRICE_PER_SQFT <= price <= MAX_PRICE_PER_SQFT
            self.assertFalse(is_valid, f"Prix {price} devrait être invalide (trop élevé)")


class TestPydanticModels(unittest.TestCase):
    """Tests des modèles Pydantic"""
    
    def test_feature_creation(self):
        """Test création d'une Feature"""
        feature = Feature(
            source_type="transaction",
            source_id="TX-001",
            record_date=date.today(),
            community="Dubai Marina",
            price_aed=Decimal("1500000"),
            price_per_sqft=Decimal("1500"),
            area_sqft=Decimal("1000")
        )
        self.assertEqual(feature.source_type, "transaction")
        self.assertEqual(feature.community, "Dubai Marina")
    
    def test_kpi_creation(self):
        """Test création d'un KPI"""
        kpi = KPI(
            calculation_date=date.today(),
            community="Dubai Marina",
            rooms_bucket="2BR",
            window_days=30,
            tls=Decimal("0.15"),
            spi=Decimal("45.0")
        )
        self.assertEqual(kpi.window_days, 30)
        self.assertIsNotNone(kpi.tls)
    
    def test_risk_summary_creation(self):
        """Test création d'un RiskSummary"""
        summary = RiskSummary(
            summary_date=date.today(),
            community="Business Bay",
            supply_risk_level="MEDIUM",
            volatility_risk_level="LOW",
            divergence_risk_level="HIGH",
            overall_risk_score=Decimal("55.0"),
            risk_factors=["High listing-transaction spread"]
        )
        self.assertEqual(summary.supply_risk_level, "MEDIUM")
        self.assertEqual(len(summary.risk_factors), 1)
    
    def test_quality_log_creation(self):
        """Test création d'un QualityLog"""
        from datetime import datetime
        
        log = QualityLog(
            run_date=datetime.now(),
            source_type="transactions",
            pipeline_step="ingestion",
            records_total=100,
            records_accepted=85,
            records_rejected=15,
            rejection_reasons={"outliers": 10, "missing_fields": 5},
            field_completeness={"price": 100.0, "area": 95.0}
        )
        self.assertEqual(log.records_accepted, 85)
        self.assertEqual(log.rejection_reasons["outliers"], 10)


class TestIntegration(unittest.TestCase):
    """Tests d'intégration (nécessitent une connexion DB)"""
    
    @unittest.skip("Nécessite une connexion DB active")
    def test_compute_features_pipeline(self):
        """Test du pipeline compute_features"""
        from pipelines.compute_features import compute_features
        
        count, quality_log = compute_features()
        
        self.assertIsNotNone(quality_log)
        self.assertEqual(quality_log.source_type, "features")
        self.assertGreaterEqual(quality_log.records_total, 0)
    
    @unittest.skip("Nécessite une connexion DB active")
    def test_compute_kpis_pipeline(self):
        """Test du pipeline compute_kpis"""
        from pipelines.compute_kpis import compute_kpis
        
        count = compute_kpis()
        self.assertGreaterEqual(count, 0)
    
    @unittest.skip("Nécessite une connexion DB active")
    def test_compute_risk_summary_pipeline(self):
        """Test du pipeline compute_risk_summary"""
        from pipelines.compute_risk_summary import compute_risk_summary
        
        count = compute_risk_summary()
        self.assertGreaterEqual(count, 0)


if __name__ == "__main__":
    # Exécuter les tests
    unittest.main(verbosity=2)
