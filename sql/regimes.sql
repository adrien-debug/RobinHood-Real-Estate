-- ====================================================================
-- CLASSIFICATION DES RÉGIMES DE MARCHÉ (institutionnel)
-- ====================================================================

CREATE OR REPLACE FUNCTION classify_market_regime(
    volume_trend VARCHAR,
    price_trend VARCHAR,
    dispersion_level VARCHAR,
    volatility_level VARCHAR
) RETURNS VARCHAR AS $$
BEGIN
    -- ACCUMULATION : volume ↑, prix stable, dispersion élevée
    IF volume_trend = 'up' AND price_trend = 'stable' AND dispersion_level = 'high' THEN
        RETURN 'ACCUMULATION';
    END IF;
    
    -- EXPANSION : volume ↑, prix ↑, dispersion ↓
    IF volume_trend = 'up' AND price_trend = 'up' AND dispersion_level = 'low' THEN
        RETURN 'EXPANSION';
    END IF;
    
    -- DISTRIBUTION : volume ↓, prix stable/haut, dispersion ↑
    IF volume_trend = 'down' AND price_trend IN ('stable', 'up') AND dispersion_level = 'high' THEN
        RETURN 'DISTRIBUTION';
    END IF;
    
    -- RETOURNEMENT : volume ↓, prix ↓, volatilité ↑
    IF volume_trend = 'down' AND price_trend = 'down' AND volatility_level = 'high' THEN
        RETURN 'RETOURNEMENT';
    END IF;
    
    -- EXPANSION (variante)
    IF volume_trend = 'up' AND price_trend = 'up' THEN
        RETURN 'EXPANSION';
    END IF;
    
    -- ACCUMULATION (variante)
    IF volume_trend = 'up' AND dispersion_level = 'high' THEN
        RETURN 'ACCUMULATION';
    END IF;
    
    -- DISTRIBUTION (variante)
    IF volume_trend = 'down' AND price_trend = 'stable' THEN
        RETURN 'DISTRIBUTION';
    END IF;
    
    -- Par défaut
    RETURN 'NEUTRAL';
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ====================================================================
-- CALCUL DES RÉGIMES
-- ====================================================================
CREATE OR REPLACE FUNCTION compute_market_regimes(target_date DATE)
RETURNS TABLE (
    community VARCHAR,
    project VARCHAR,
    building VARCHAR,
    regime VARCHAR,
    confidence_score DECIMAL,
    volume_trend VARCHAR,
    price_trend VARCHAR,
    dispersion_level VARCHAR,
    volatility_level VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    WITH current_metrics AS (
        SELECT 
            mb.community,
            mb.project,
            mb.building,
            mb.transaction_count,
            mb.momentum,
            mb.dispersion,
            mb.volatility
        FROM market_baselines mb
        WHERE mb.calculation_date = target_date
            AND mb.window_days = 30
    ),
    previous_metrics AS (
        SELECT 
            mb.community,
            mb.project,
            mb.building,
            mb.transaction_count as prev_count
        FROM market_baselines mb
        WHERE mb.calculation_date = target_date - 30
            AND mb.window_days = 30
    ),
    trends AS (
        SELECT 
            cm.community,
            cm.project,
            cm.building,
            -- Volume trend
            CASE 
                WHEN pm.prev_count IS NULL THEN 'stable'
                WHEN cm.transaction_count > pm.prev_count * 1.2 THEN 'up'
                WHEN cm.transaction_count < pm.prev_count * 0.8 THEN 'down'
                ELSE 'stable'
            END as vol_trend,
            -- Price trend (momentum)
            CASE 
                WHEN cm.momentum > 0.05 THEN 'up'
                WHEN cm.momentum < -0.05 THEN 'down'
                ELSE 'stable'
            END as price_trend,
            -- Dispersion level
            CASE 
                WHEN cm.dispersion > 0.25 THEN 'high'
                WHEN cm.dispersion > 0.15 THEN 'medium'
                ELSE 'low'
            END as disp_level,
            -- Volatility level
            CASE 
                WHEN cm.volatility > 0.20 THEN 'high'
                WHEN cm.volatility > 0.10 THEN 'medium'
                ELSE 'low'
            END as vol_level,
            cm.transaction_count,
            cm.momentum,
            cm.dispersion,
            cm.volatility
        FROM current_metrics cm
        LEFT JOIN previous_metrics pm ON 
            cm.community = pm.community 
            AND cm.project = pm.project 
            AND cm.building = pm.building
    )
    SELECT 
        t.community,
        t.project,
        t.building,
        classify_market_regime(t.vol_trend, t.price_trend, t.disp_level, t.vol_level) as regime,
        -- Confidence score basé sur le volume de données
        CASE 
            WHEN t.transaction_count >= 30 THEN 0.95
            WHEN t.transaction_count >= 15 THEN 0.80
            WHEN t.transaction_count >= 5 THEN 0.60
            ELSE 0.40
        END::DECIMAL(5,4) as confidence_score,
        t.vol_trend,
        t.price_trend,
        t.disp_level,
        t.vol_level
    FROM trends t
    WHERE t.transaction_count >= 3;
END;
$$ LANGUAGE plpgsql;

-- ====================================================================
-- INSERTION DES RÉGIMES
-- ====================================================================
CREATE OR REPLACE PROCEDURE refresh_market_regimes(target_date DATE DEFAULT CURRENT_DATE)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO market_regimes (
        regime_date, community, project, building, regime, confidence_score,
        volume_trend, price_trend, dispersion_level, volatility_level
    )
    SELECT 
        target_date, community, project, building, regime, confidence_score,
        volume_trend, price_trend, dispersion_level, volatility_level
    FROM compute_market_regimes(target_date)
    ON CONFLICT (regime_date, community, project, building)
    DO UPDATE SET
        regime = EXCLUDED.regime,
        confidence_score = EXCLUDED.confidence_score,
        volume_trend = EXCLUDED.volume_trend,
        price_trend = EXCLUDED.price_trend,
        dispersion_level = EXCLUDED.dispersion_level,
        volatility_level = EXCLUDED.volatility_level;

    RAISE NOTICE 'Market regimes refreshed for %', target_date;
END;
$$;
