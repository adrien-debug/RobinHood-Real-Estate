-- ====================================================================
-- DÉTECTION D'OPPORTUNITÉS
-- ====================================================================

CREATE OR REPLACE FUNCTION detect_opportunities(target_date DATE)
RETURNS TABLE (
    transaction_id UUID,
    community VARCHAR,
    project VARCHAR,
    building VARCHAR,
    rooms_bucket VARCHAR,
    price_per_sqft DECIMAL,
    market_median_sqft DECIMAL,
    discount_pct DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id as transaction_id,
        t.community,
        t.project,
        t.building,
        t.rooms_bucket,
        t.price_per_sqft,
        mb.median_price_per_sqft as market_median_sqft,
        ((mb.median_price_per_sqft - t.price_per_sqft) / mb.median_price_per_sqft * 100)::DECIMAL(6,2) as discount_pct
    FROM transactions t
    INNER JOIN market_baselines mb ON 
        t.community = mb.community 
        AND COALESCE(t.project, '') = COALESCE(mb.project, '')
        AND t.rooms_bucket = mb.rooms_bucket
        AND mb.calculation_date = target_date
        AND mb.window_days = 30
    WHERE t.transaction_date = target_date
        AND t.price_per_sqft < mb.median_price_per_sqft * 0.90  -- 10% sous marché minimum
        AND t.price_per_sqft > 0
        AND mb.transaction_count >= 5  -- liquidité minimum
    ORDER BY discount_pct DESC;
END;
$$ LANGUAGE plpgsql;
