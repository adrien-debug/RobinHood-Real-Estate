-- ====================================================================
-- CALCUL DES BASELINES MARCHÉ (rolling metrics)
-- ====================================================================

-- Fonction : calculer baselines pour une date donnée
CREATE OR REPLACE FUNCTION compute_market_baselines(target_date DATE, window_days INTEGER)
RETURNS TABLE (
    community VARCHAR,
    project VARCHAR,
    building VARCHAR,
    rooms_bucket VARCHAR,
    median_price_per_sqft DECIMAL,
    p25_price_per_sqft DECIMAL,
    p75_price_per_sqft DECIMAL,
    avg_price_per_sqft DECIMAL,
    transaction_count INTEGER,
    total_volume_aed DECIMAL,
    momentum DECIMAL,
    volatility DECIMAL,
    dispersion DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    WITH current_window AS (
        SELECT 
            t.community,
            t.project,
            t.building,
            t.rooms_bucket,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY t.price_per_sqft) as median_sqft,
            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY t.price_per_sqft) as p25_sqft,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY t.price_per_sqft) as p75_sqft,
            AVG(t.price_per_sqft) as avg_sqft,
            COUNT(*) as tx_count,
            SUM(t.price_aed) as volume,
            STDDEV(t.price_per_sqft) as std_dev,
            (PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY t.price_per_sqft) - 
             PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY t.price_per_sqft)) as iqr
        FROM transactions t
        WHERE t.transaction_date BETWEEN (target_date - window_days) AND target_date
            AND t.price_per_sqft IS NOT NULL
            AND t.price_per_sqft > 0
        GROUP BY t.community, t.project, t.building, t.rooms_bucket
        HAVING COUNT(*) >= 3
    ),
    previous_window AS (
        SELECT 
            t.community,
            t.project,
            t.building,
            t.rooms_bucket,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY t.price_per_sqft) as prev_median_sqft
        FROM transactions t
        WHERE t.transaction_date BETWEEN (target_date - 2*window_days) AND (target_date - window_days)
            AND t.price_per_sqft IS NOT NULL
            AND t.price_per_sqft > 0
        GROUP BY t.community, t.project, t.building, t.rooms_bucket
    )
    SELECT 
        cw.community,
        cw.project,
        cw.building,
        cw.rooms_bucket,
        cw.median_sqft::DECIMAL(10,2),
        cw.p25_sqft::DECIMAL(10,2),
        cw.p75_sqft::DECIMAL(10,2),
        cw.avg_sqft::DECIMAL(10,2),
        cw.tx_count::INTEGER,
        cw.volume::DECIMAL(15,2),
        CASE 
            WHEN pw.prev_median_sqft IS NOT NULL AND pw.prev_median_sqft > 0 
            THEN ((cw.median_sqft - pw.prev_median_sqft) / pw.prev_median_sqft)::DECIMAL(8,4)
            ELSE NULL
        END as momentum,
        CASE 
            WHEN cw.median_sqft > 0 
            THEN (cw.std_dev / cw.median_sqft)::DECIMAL(8,4)
            ELSE NULL
        END as volatility,
        CASE 
            WHEN cw.median_sqft > 0 
            THEN (cw.iqr / cw.median_sqft)::DECIMAL(8,4)
            ELSE NULL
        END as dispersion
    FROM current_window cw
    LEFT JOIN previous_window pw ON 
        cw.community = pw.community 
        AND cw.project = pw.project 
        AND cw.building = pw.building
        AND cw.rooms_bucket = pw.rooms_bucket;
END;
$$ LANGUAGE plpgsql;

-- ====================================================================
-- INSERTION DES BASELINES
-- ====================================================================
CREATE OR REPLACE PROCEDURE refresh_market_baselines(target_date DATE DEFAULT CURRENT_DATE)
LANGUAGE plpgsql
AS $$
BEGIN
    -- 7 jours
    INSERT INTO market_baselines (
        calculation_date, community, project, building, rooms_bucket, window_days,
        median_price_per_sqft, p25_price_per_sqft, p75_price_per_sqft, avg_price_per_sqft,
        transaction_count, total_volume_aed, momentum, volatility, dispersion
    )
    SELECT 
        target_date, community, project, building, rooms_bucket, 7,
        median_price_per_sqft, p25_price_per_sqft, p75_price_per_sqft, avg_price_per_sqft,
        transaction_count, total_volume_aed, momentum, volatility, dispersion
    FROM compute_market_baselines(target_date, 7)
    ON CONFLICT (calculation_date, community, project, building, rooms_bucket, window_days)
    DO UPDATE SET
        median_price_per_sqft = EXCLUDED.median_price_per_sqft,
        p25_price_per_sqft = EXCLUDED.p25_price_per_sqft,
        p75_price_per_sqft = EXCLUDED.p75_price_per_sqft,
        avg_price_per_sqft = EXCLUDED.avg_price_per_sqft,
        transaction_count = EXCLUDED.transaction_count,
        total_volume_aed = EXCLUDED.total_volume_aed,
        momentum = EXCLUDED.momentum,
        volatility = EXCLUDED.volatility,
        dispersion = EXCLUDED.dispersion;

    -- 30 jours
    INSERT INTO market_baselines (
        calculation_date, community, project, building, rooms_bucket, window_days,
        median_price_per_sqft, p25_price_per_sqft, p75_price_per_sqft, avg_price_per_sqft,
        transaction_count, total_volume_aed, momentum, volatility, dispersion
    )
    SELECT 
        target_date, community, project, building, rooms_bucket, 30,
        median_price_per_sqft, p25_price_per_sqft, p75_price_per_sqft, avg_price_per_sqft,
        transaction_count, total_volume_aed, momentum, volatility, dispersion
    FROM compute_market_baselines(target_date, 30)
    ON CONFLICT (calculation_date, community, project, building, rooms_bucket, window_days)
    DO UPDATE SET
        median_price_per_sqft = EXCLUDED.median_price_per_sqft,
        p25_price_per_sqft = EXCLUDED.p25_price_per_sqft,
        p75_price_per_sqft = EXCLUDED.p75_price_per_sqft,
        avg_price_per_sqft = EXCLUDED.avg_price_per_sqft,
        transaction_count = EXCLUDED.transaction_count,
        total_volume_aed = EXCLUDED.total_volume_aed,
        momentum = EXCLUDED.momentum,
        volatility = EXCLUDED.volatility,
        dispersion = EXCLUDED.dispersion;

    -- 90 jours
    INSERT INTO market_baselines (
        calculation_date, community, project, building, rooms_bucket, window_days,
        median_price_per_sqft, p25_price_per_sqft, p75_price_per_sqft, avg_price_per_sqft,
        transaction_count, total_volume_aed, momentum, volatility, dispersion
    )
    SELECT 
        target_date, community, project, building, rooms_bucket, 90,
        median_price_per_sqft, p25_price_per_sqft, p75_price_per_sqft, avg_price_per_sqft,
        transaction_count, total_volume_aed, momentum, volatility, dispersion
    FROM compute_market_baselines(target_date, 90)
    ON CONFLICT (calculation_date, community, project, building, rooms_bucket, window_days)
    DO UPDATE SET
        median_price_per_sqft = EXCLUDED.median_price_per_sqft,
        p25_price_per_sqft = EXCLUDED.p25_price_per_sqft,
        p75_price_per_sqft = EXCLUDED.p75_price_per_sqft,
        avg_price_per_sqft = EXCLUDED.avg_price_per_sqft,
        transaction_count = EXCLUDED.transaction_count,
        total_volume_aed = EXCLUDED.total_volume_aed,
        momentum = EXCLUDED.momentum,
        volatility = EXCLUDED.volatility,
        dispersion = EXCLUDED.dispersion;

    RAISE NOTICE 'Baselines refreshed for %', target_date;
END;
$$;
