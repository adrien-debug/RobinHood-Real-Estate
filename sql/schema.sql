-- ====================================================================
-- DUBAI REAL ESTATE INTELLIGENCE — SCHEMA PostgreSQL
-- ====================================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Schema (évite les conflits avec tables existantes)
CREATE SCHEMA IF NOT EXISTS robin;
SET search_path TO robin, public;

-- ====================================================================
-- TRANSACTIONS (DLD)
-- ====================================================================
CREATE TABLE IF NOT EXISTS robin.transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(50), -- sale, mortgage, gift
    
    -- Location
    community VARCHAR(255),
    project VARCHAR(255),
    building VARCHAR(255),
    unit_number VARCHAR(100),
    
    -- Property
    property_type VARCHAR(100), -- apartment, villa, townhouse
    property_subtype VARCHAR(100),
    rooms_count INTEGER,
    rooms_bucket VARCHAR(20), -- studio, 1BR, 2BR, 3BR+
    area_sqft DECIMAL(10, 2),
    
    -- Price
    price_aed DECIMAL(15, 2),
    price_per_sqft DECIMAL(10, 2),
    
    -- Parties
    buyer_name VARCHAR(255),
    seller_name VARCHAR(255),
    is_offplan BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transaction_date ON robin.transactions (transaction_date DESC);
CREATE INDEX IF NOT EXISTS idx_community ON robin.transactions (community);
CREATE INDEX IF NOT EXISTS idx_project ON robin.transactions (project);
CREATE INDEX IF NOT EXISTS idx_building ON robin.transactions (building);
CREATE INDEX IF NOT EXISTS idx_rooms_bucket ON robin.transactions (rooms_bucket);
CREATE INDEX IF NOT EXISTS idx_price_per_sqft ON robin.transactions (price_per_sqft);

-- ====================================================================
-- MORTGAGES (DLD)
-- ====================================================================
CREATE TABLE IF NOT EXISTS robin.mortgages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mortgage_id VARCHAR(255) UNIQUE NOT NULL,
    mortgage_date DATE NOT NULL,
    
    -- Property reference
    community VARCHAR(255),
    project VARCHAR(255),
    building VARCHAR(255),
    
    -- Mortgage details
    mortgage_amount_aed DECIMAL(15, 2),
    lender VARCHAR(255),
    borrower VARCHAR(255),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mortgage_date ON robin.mortgages (mortgage_date DESC);
CREATE INDEX IF NOT EXISTS idx_community_mortgage ON robin.mortgages (community);

-- ====================================================================
-- RENTAL INDEX (DLD)
-- ====================================================================
CREATE TABLE IF NOT EXISTS robin.rental_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    period_date DATE NOT NULL,
    
    -- Location
    community VARCHAR(255),
    project VARCHAR(255),
    
    -- Property
    property_type VARCHAR(100),
    rooms_bucket VARCHAR(20),
    
    -- Rental data
    avg_rent_aed DECIMAL(12, 2),
    median_rent_aed DECIMAL(12, 2),
    rent_count INTEGER,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE (period_date, community, project, property_type, rooms_bucket)
);

CREATE INDEX IF NOT EXISTS idx_rental_period ON robin.rental_index (period_date DESC);
CREATE INDEX IF NOT EXISTS idx_rental_community ON robin.rental_index (community);

-- ====================================================================
-- DEVELOPERS PIPELINE (supply future)
-- ====================================================================
CREATE TABLE IF NOT EXISTS robin.developers_pipeline (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_name VARCHAR(255) NOT NULL,
    developer VARCHAR(255),
    
    -- Location
    community VARCHAR(255),
    
    -- Supply
    total_units INTEGER,
    units_by_type JSONB, -- {"studio": 50, "1BR": 200, ...}
    
    -- Timeline
    launch_date DATE,
    expected_handover_date DATE,
    actual_handover_date DATE,
    
    -- Status
    status VARCHAR(50), -- planned, under_construction, delivered
    completion_percentage DECIMAL(5, 2),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_handover_date ON robin.developers_pipeline (expected_handover_date);
CREATE INDEX IF NOT EXISTS idx_developer_community ON robin.developers_pipeline (community);

-- ====================================================================
-- LISTINGS (annonces autorisées)
-- ====================================================================
CREATE TABLE IF NOT EXISTS robin.listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id VARCHAR(255) UNIQUE NOT NULL,
    listing_date DATE NOT NULL,
    
    -- Location
    community VARCHAR(255),
    project VARCHAR(255),
    building VARCHAR(255),
    
    -- Property
    property_type VARCHAR(100),
    rooms_bucket VARCHAR(20),
    area_sqft DECIMAL(10, 2),
    
    -- Price
    asking_price_aed DECIMAL(15, 2),
    asking_price_per_sqft DECIMAL(10, 2),
    
    -- History
    original_price_aed DECIMAL(15, 2),
    price_changes INTEGER DEFAULT 0,
    last_price_change_date DATE,
    days_on_market INTEGER,
    
    -- Status
    status VARCHAR(50), -- active, sold, withdrawn
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_listing_date ON robin.listings (listing_date DESC);
CREATE INDEX IF NOT EXISTS idx_listing_community ON robin.listings (community);
CREATE INDEX IF NOT EXISTS idx_listing_status ON robin.listings (status);

-- ====================================================================
-- MARKET BASELINES (rolling metrics)
-- ====================================================================
CREATE TABLE IF NOT EXISTS robin.market_baselines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    calculation_date DATE NOT NULL,
    
    -- Scope
    community VARCHAR(255),
    project VARCHAR(255),
    building VARCHAR(255),
    rooms_bucket VARCHAR(20),
    
    -- Time window
    window_days INTEGER, -- 7, 30, 90
    
    -- Price metrics
    median_price_per_sqft DECIMAL(10, 2),
    p25_price_per_sqft DECIMAL(10, 2),
    p75_price_per_sqft DECIMAL(10, 2),
    avg_price_per_sqft DECIMAL(10, 2),
    
    -- Volume
    transaction_count INTEGER,
    total_volume_aed DECIMAL(15, 2),
    
    -- Dynamics
    momentum DECIMAL(8, 4), -- % change vs previous period
    volatility DECIMAL(8, 4), -- std dev
    dispersion DECIMAL(8, 4), -- IQR / median
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE (calculation_date, community, project, building, rooms_bucket, window_days)
);

CREATE INDEX IF NOT EXISTS idx_baseline_date ON robin.market_baselines (calculation_date DESC);
CREATE INDEX IF NOT EXISTS idx_baseline_scope ON robin.market_baselines (community, project, building);

-- ====================================================================
-- MARKET REGIMES (classification institutionnelle)
-- ====================================================================
CREATE TABLE IF NOT EXISTS robin.market_regimes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    regime_date DATE NOT NULL,
    
    -- Scope
    community VARCHAR(255),
    project VARCHAR(255),
    building VARCHAR(255),
    
    -- Regime classification
    regime VARCHAR(50), -- ACCUMULATION, EXPANSION, DISTRIBUTION, RETOURNEMENT
    confidence_score DECIMAL(5, 4), -- 0-1
    
    -- Signals
    volume_trend VARCHAR(20), -- up, down, stable
    price_trend VARCHAR(20),
    dispersion_level VARCHAR(20), -- low, medium, high
    volatility_level VARCHAR(20),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_regime_date ON robin.market_regimes (regime_date DESC);
CREATE INDEX IF NOT EXISTS idx_regime_type ON robin.market_regimes (regime);
CREATE INDEX IF NOT EXISTS idx_regime_scope ON robin.market_regimes (community, project);

-- ====================================================================
-- OPPORTUNITIES (deals détectés)
-- ====================================================================
CREATE TABLE IF NOT EXISTS robin.opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    detection_date DATE NOT NULL,
    
    -- Property reference
    transaction_id UUID REFERENCES robin.transactions(id),
    listing_id UUID REFERENCES robin.listings(id),
    
    -- Location
    community VARCHAR(255),
    project VARCHAR(255),
    building VARCHAR(255),
    rooms_bucket VARCHAR(20),
    
    -- Metrics
    price_per_sqft DECIMAL(10, 2),
    market_median_sqft DECIMAL(10, 2),
    discount_pct DECIMAL(6, 2), -- % sous marché
    
    -- Scores
    global_score DECIMAL(6, 2), -- 0-100
    flip_score DECIMAL(6, 2),
    rent_score DECIMAL(6, 2),
    long_term_score DECIMAL(6, 2),
    
    -- Recommendation
    recommended_strategy VARCHAR(50), -- FLIP, RENT, LONG, IGNORE
    
    -- Context
    market_regime VARCHAR(50),
    liquidity_score DECIMAL(6, 2),
    supply_risk VARCHAR(20), -- low, medium, high
    
    -- Status
    status VARCHAR(50) DEFAULT 'active', -- active, reviewed, dismissed
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_opp_date ON robin.opportunities (detection_date DESC);
CREATE INDEX IF NOT EXISTS idx_opp_score ON robin.opportunities (global_score DESC);
CREATE INDEX IF NOT EXISTS idx_opp_strategy ON robin.opportunities (recommended_strategy);
CREATE INDEX IF NOT EXISTS idx_opp_status ON robin.opportunities (status);

-- ====================================================================
-- ALERTS
-- ====================================================================
CREATE TABLE IF NOT EXISTS robin.alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_date TIMESTAMP DEFAULT NOW(),
    
    -- Alert type
    alert_type VARCHAR(100), -- price_drop, regime_change, new_opportunity
    severity VARCHAR(20), -- low, medium, high, critical
    
    -- Content
    title VARCHAR(255),
    message TEXT,
    
    -- Reference
    opportunity_id UUID REFERENCES robin.opportunities(id),
    community VARCHAR(255),
    
    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    is_dismissed BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alert_date ON robin.alerts (alert_date DESC);
CREATE INDEX IF NOT EXISTS idx_alert_type ON robin.alerts (alert_type);
CREATE INDEX IF NOT EXISTS idx_alert_status ON robin.alerts (is_read, is_dismissed);

-- ====================================================================
-- DAILY BRIEFS (CIO Agent)
-- ====================================================================
CREATE TABLE IF NOT EXISTS robin.daily_briefs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brief_date DATE UNIQUE NOT NULL,
    
    -- Content
    zones_to_watch JSONB, -- [{zone, reason}, ...]
    top_opportunities JSONB, -- [{opp_id, reason}, ...]
    main_risk TEXT,
    strategic_recommendation TEXT,
    
    -- Full brief
    full_brief_text TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_brief_date ON robin.daily_briefs (brief_date DESC);

-- ====================================================================
-- VIEWS
-- ====================================================================

-- Vue : transactions récentes avec contexte marché
CREATE OR REPLACE VIEW robin.v_recent_transactions AS
SELECT 
    t.*,
    mb.median_price_per_sqft as market_median_30d,
    ((t.price_per_sqft - mb.median_price_per_sqft) / mb.median_price_per_sqft * 100) as discount_pct,
    mr.regime as market_regime
FROM robin.transactions t
LEFT JOIN robin.market_baselines mb ON 
    t.community = mb.community 
    AND t.rooms_bucket = mb.rooms_bucket
    AND mb.window_days = 30
    AND mb.calculation_date = CURRENT_DATE
LEFT JOIN robin.market_regimes mr ON
    t.community = mr.community
    AND mr.regime_date = CURRENT_DATE
WHERE t.transaction_date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY t.transaction_date DESC;

-- Vue : opportunités actives avec détails
CREATE OR REPLACE VIEW robin.v_active_opportunities AS
SELECT 
    o.*,
    t.transaction_date,
    t.property_type,
    t.area_sqft,
    mr.regime as current_regime,
    mr.confidence_score as regime_confidence
FROM robin.opportunities o
LEFT JOIN robin.transactions t ON o.transaction_id = t.id
LEFT JOIN robin.market_regimes mr ON 
    o.community = mr.community 
    AND mr.regime_date = CURRENT_DATE
WHERE o.status = 'active'
ORDER BY o.global_score DESC;
