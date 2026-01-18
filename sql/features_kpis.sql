-- ====================================================================
-- TABLES FEATURES, KPIs, QUALITY LOGS, RISK SUMMARIES
-- Pipeline de données avancé pour l'analyse immobilière Dubai
-- ====================================================================

-- ====================================================================
-- FEATURES (données normalisées + features dérivées)
-- ====================================================================
CREATE TABLE IF NOT EXISTS robin.features (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Source
    source_type VARCHAR(20) NOT NULL, -- 'transaction' ou 'listing'
    source_id VARCHAR(255) NOT NULL, -- ID original (transaction_id ou listing_id)
    record_date DATE NOT NULL,
    
    -- Localisation normalisée
    community VARCHAR(255),
    project VARCHAR(255),
    building VARCHAR(255),
    rooms_bucket VARCHAR(20), -- studio, 1BR, 2BR, 3BR+
    property_type VARCHAR(100),
    
    -- Prix normalisés (AED)
    price_aed DECIMAL(15, 2),
    price_per_sqft DECIMAL(10, 2),
    area_sqft DECIMAL(10, 2),
    
    -- Features dérivées
    is_offplan BOOLEAN DEFAULT FALSE,
    days_on_market INTEGER,
    price_change_count INTEGER DEFAULT 0,
    
    -- Geo-features Makani
    makani_number VARCHAR(20),
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    metro_distance_m INTEGER,
    beach_distance_m INTEGER,
    mall_distance_m INTEGER,
    location_score DECIMAL(5, 2), -- 0-100
    
    -- Métadonnées
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Contrainte pour éviter les outliers
    CONSTRAINT chk_price_per_sqft CHECK (
        price_per_sqft IS NULL OR 
        (price_per_sqft >= 500 AND price_per_sqft <= 10000)
    ),
    
    -- Unicité par source
    UNIQUE (source_type, source_id)
);

CREATE INDEX IF NOT EXISTS idx_features_date ON robin.features (record_date DESC);
CREATE INDEX IF NOT EXISTS idx_features_community ON robin.features (community);
CREATE INDEX IF NOT EXISTS idx_features_source_type ON robin.features (source_type);
CREATE INDEX IF NOT EXISTS idx_features_price_sqft ON robin.features (price_per_sqft);
CREATE INDEX IF NOT EXISTS idx_features_rooms ON robin.features (rooms_bucket);

-- ====================================================================
-- KPIs (8 KPIs avancés)
-- ====================================================================
CREATE TABLE IF NOT EXISTS robin.kpis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calculation_date DATE NOT NULL,
    
    -- Scope
    community VARCHAR(255),
    project VARCHAR(255),
    rooms_bucket VARCHAR(20),
    window_days INTEGER NOT NULL, -- 7, 30, 90
    
    -- KPIs calculés
    tls DECIMAL(8, 4), -- Transaction-to-Listing Spread
    lad DECIMAL(8, 4), -- Liquidity-Adjusted Discount
    rsg DECIMAL(8, 4), -- Rental Stress Gap
    spi DECIMAL(8, 4), -- Supply Pressure Index (0-100)
    gpi DECIMAL(8, 4), -- Geo-Premium Index
    rcwm DECIMAL(8, 4), -- Regime Confidence-Weighted Momentum
    ord DECIMAL(8, 4), -- Offplan Risk Delta
    aps DECIMAL(8, 4), -- Anomaly Persistence Score
    
    -- Données sources (pour traçabilité)
    median_tx_psf DECIMAL(10, 2),
    median_listing_psf DECIMAL(10, 2),
    tx_count INTEGER,
    listing_count INTEGER,
    planned_units_12m INTEGER,
    median_rent_aed DECIMAL(12, 2),
    
    -- Métadonnées
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE (calculation_date, community, project, rooms_bucket, window_days)
);

CREATE INDEX IF NOT EXISTS idx_kpis_date ON robin.kpis (calculation_date DESC);
CREATE INDEX IF NOT EXISTS idx_kpis_community ON robin.kpis (community);
CREATE INDEX IF NOT EXISTS idx_kpis_window ON robin.kpis (window_days);

-- ====================================================================
-- QUALITY LOGS (logs de qualité des données)
-- ====================================================================
CREATE TABLE IF NOT EXISTS robin.quality_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_date TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Source
    source_type VARCHAR(50) NOT NULL, -- 'transactions', 'listings', 'rental_index', etc.
    pipeline_step VARCHAR(100), -- 'ingestion', 'normalization', 'feature_computation'
    
    -- Métriques de volume
    records_total INTEGER NOT NULL DEFAULT 0,
    records_accepted INTEGER NOT NULL DEFAULT 0,
    records_rejected INTEGER NOT NULL DEFAULT 0,
    
    -- Raisons de rejet (JSONB)
    rejection_reasons JSONB DEFAULT '{}'::jsonb,
    -- Format: {"outliers": 15, "duplicates": 3, "missing_fields": 8, "invalid_price": 2}
    
    -- Complétude des champs (JSONB)
    field_completeness JSONB DEFAULT '{}'::jsonb,
    -- Format: {"community": 98.5, "price": 100, "area": 95.2, ...}
    
    -- Durée d'exécution
    execution_time_ms INTEGER,
    
    -- Statut
    status VARCHAR(20) DEFAULT 'success', -- 'success', 'warning', 'error'
    error_message TEXT,
    
    -- Métadonnées
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quality_logs_date ON robin.quality_logs (run_date DESC);
CREATE INDEX IF NOT EXISTS idx_quality_logs_source ON robin.quality_logs (source_type);
CREATE INDEX IF NOT EXISTS idx_quality_logs_status ON robin.quality_logs (status);

-- ====================================================================
-- RISK SUMMARIES (résumé des risques par zone)
-- ====================================================================
CREATE TABLE IF NOT EXISTS robin.risk_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    summary_date DATE NOT NULL,
    
    -- Scope
    community VARCHAR(255) NOT NULL,
    project VARCHAR(255),
    
    -- Niveaux de risque
    supply_risk_level VARCHAR(20), -- 'LOW', 'MEDIUM', 'HIGH'
    volatility_risk_level VARCHAR(20), -- 'LOW', 'MEDIUM', 'HIGH'
    divergence_risk_level VARCHAR(20), -- 'LOW', 'MEDIUM', 'HIGH'
    
    -- Métriques détaillées
    supply_spi DECIMAL(8, 4),
    volatility_pct DECIMAL(8, 4),
    listing_tx_divergence_pct DECIMAL(8, 4), -- écart listing vs transaction
    
    -- Score global de risque
    overall_risk_score DECIMAL(5, 2), -- 0-100
    
    -- Commentaires automatiques
    risk_factors JSONB DEFAULT '[]'::jsonb,
    -- Format: ["High supply in next 12 months", "Price volatility above 25%", ...]
    
    -- Métadonnées
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE (summary_date, community, project)
);

CREATE INDEX IF NOT EXISTS idx_risk_date ON robin.risk_summaries (summary_date DESC);
CREATE INDEX IF NOT EXISTS idx_risk_community ON robin.risk_summaries (community);
CREATE INDEX IF NOT EXISTS idx_risk_level ON robin.risk_summaries (overall_risk_score DESC);

-- ====================================================================
-- FONCTIONS UTILITAIRES
-- ====================================================================

-- Fonction : Calculer TLS (Transaction-to-Listing Spread)
CREATE OR REPLACE FUNCTION robin.calc_tls(
    median_listing_psf DECIMAL,
    median_tx_psf DECIMAL
) RETURNS DECIMAL AS $$
BEGIN
    IF median_tx_psf IS NULL OR median_tx_psf = 0 THEN
        RETURN NULL;
    END IF;
    RETURN (median_listing_psf - median_tx_psf) / median_tx_psf;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Fonction : Calculer LAD (Liquidity-Adjusted Discount)
CREATE OR REPLACE FUNCTION robin.calc_lad(
    discount_pct DECIMAL,
    tx_count INTEGER
) RETURNS DECIMAL AS $$
BEGIN
    IF discount_pct IS NULL OR tx_count IS NULL THEN
        RETURN NULL;
    END IF;
    RETURN discount_pct * LN(1 + tx_count);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Fonction : Calculer RSG (Rental Stress Gap)
CREATE OR REPLACE FUNCTION robin.calc_rsg(
    median_rent DECIMAL,
    price_psf DECIMAL,
    avg_sqft DECIMAL,
    target_yield DECIMAL DEFAULT 0.06
) RETURNS DECIMAL AS $$
DECLARE
    expected_rent DECIMAL;
BEGIN
    IF price_psf IS NULL OR avg_sqft IS NULL OR price_psf = 0 THEN
        RETURN NULL;
    END IF;
    expected_rent := price_psf * avg_sqft * target_yield;
    IF expected_rent = 0 THEN
        RETURN NULL;
    END IF;
    RETURN (median_rent - expected_rent) / expected_rent;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Fonction : Calculer SPI (Supply Pressure Index) normalisé 0-100
CREATE OR REPLACE FUNCTION robin.calc_spi(
    planned_units_12m INTEGER,
    tx_count_12m INTEGER
) RETURNS DECIMAL AS $$
DECLARE
    raw_ratio DECIMAL;
BEGIN
    IF tx_count_12m IS NULL OR tx_count_12m = 0 THEN
        RETURN 50; -- Valeur neutre si pas de données
    END IF;
    raw_ratio := COALESCE(planned_units_12m, 0)::DECIMAL / tx_count_12m;
    -- Normalisation : ratio de 2+ = 100, ratio de 0 = 0
    RETURN LEAST(100, GREATEST(0, raw_ratio * 50));
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Fonction : Calculer RCWM (Regime Confidence-Weighted Momentum)
CREATE OR REPLACE FUNCTION robin.calc_rcwm(
    momentum DECIMAL,
    regime_confidence DECIMAL
) RETURNS DECIMAL AS $$
BEGIN
    IF momentum IS NULL OR regime_confidence IS NULL THEN
        RETURN NULL;
    END IF;
    RETURN momentum * regime_confidence;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Fonction : Calculer ORD (Offplan Risk Delta)
CREATE OR REPLACE FUNCTION robin.calc_ord(
    median_offplan_psf DECIMAL,
    median_ready_psf DECIMAL
) RETURNS DECIMAL AS $$
BEGIN
    IF median_ready_psf IS NULL OR median_ready_psf = 0 THEN
        RETURN NULL;
    END IF;
    RETURN (median_offplan_psf / median_ready_psf) - 1;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Fonction : Calculer APS (Anomaly Persistence Score)
CREATE OR REPLACE FUNCTION robin.calc_aps(
    days_anomaly_active INTEGER,
    window_days INTEGER
) RETURNS DECIMAL AS $$
BEGIN
    IF window_days IS NULL OR window_days = 0 THEN
        RETURN NULL;
    END IF;
    RETURN COALESCE(days_anomaly_active, 0)::DECIMAL / window_days;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Fonction : Déterminer le niveau de risque
CREATE OR REPLACE FUNCTION robin.get_risk_level(
    value DECIMAL,
    low_threshold DECIMAL,
    high_threshold DECIMAL
) RETURNS VARCHAR AS $$
BEGIN
    IF value IS NULL THEN
        RETURN 'UNKNOWN';
    ELSIF value < low_threshold THEN
        RETURN 'LOW';
    ELSIF value <= high_threshold THEN
        RETURN 'MEDIUM';
    ELSE
        RETURN 'HIGH';
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ====================================================================
-- VUES
-- ====================================================================

-- Vue : KPIs les plus récents par communauté
CREATE OR REPLACE VIEW robin.v_latest_kpis AS
SELECT DISTINCT ON (community, rooms_bucket, window_days)
    k.*
FROM robin.kpis k
ORDER BY community, rooms_bucket, window_days, calculation_date DESC;

-- Vue : Résumé qualité des dernières 24h
CREATE OR REPLACE VIEW robin.v_quality_summary_24h AS
SELECT 
    source_type,
    COUNT(*) as run_count,
    SUM(records_total) as total_records,
    SUM(records_accepted) as total_accepted,
    SUM(records_rejected) as total_rejected,
    ROUND(AVG(records_accepted::DECIMAL / NULLIF(records_total, 0) * 100), 2) as avg_acceptance_rate,
    COUNT(*) FILTER (WHERE status = 'error') as error_count
FROM robin.quality_logs
WHERE run_date >= NOW() - INTERVAL '24 hours'
GROUP BY source_type;

-- Vue : Risques élevés actifs
CREATE OR REPLACE VIEW robin.v_high_risk_zones AS
SELECT 
    r.*
FROM robin.risk_summaries r
WHERE r.summary_date = CURRENT_DATE
    AND (
        r.supply_risk_level = 'HIGH' 
        OR r.volatility_risk_level = 'HIGH'
        OR r.divergence_risk_level = 'HIGH'
        OR r.overall_risk_score >= 70
    )
ORDER BY r.overall_risk_score DESC;

-- Vue : Features avec contexte marché
CREATE OR REPLACE VIEW robin.v_features_with_market AS
SELECT 
    f.*,
    mb.median_price_per_sqft as market_median_30d,
    CASE 
        WHEN mb.median_price_per_sqft > 0 THEN
            ((f.price_per_sqft - mb.median_price_per_sqft) / mb.median_price_per_sqft * 100)
        ELSE NULL
    END as discount_vs_market_pct,
    mr.regime as market_regime,
    mr.confidence_score as regime_confidence
FROM robin.features f
LEFT JOIN robin.market_baselines mb ON 
    f.community = mb.community 
    AND f.rooms_bucket = mb.rooms_bucket
    AND mb.window_days = 30
    AND mb.calculation_date = CURRENT_DATE
LEFT JOIN robin.market_regimes mr ON
    f.community = mr.community
    AND mr.regime_date = CURRENT_DATE
WHERE f.record_date >= CURRENT_DATE - INTERVAL '30 days';
