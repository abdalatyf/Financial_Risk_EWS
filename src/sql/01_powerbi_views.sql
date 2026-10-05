-- =========================================================================
-- SVB Early Warning System (EWS) - Power BI Analytical Views
-- Developer: [CS Student 3 Name]
-- Description: This script creates pre-joined, optimized views for Power BI 
--              so the dashboard developer doesn't have to write complex DAX.
-- =========================================================================

USE Financial_Risk_EWS_db;

-- 1. MASTER FINANCIALS VIEW (Long Format)
-- Joins all dimensions to the fact table for easy filtering in Power BI
CREATE OR REPLACE VIEW vw_master_financials AS
SELECT 
    b.bank_name,
    b.ticker,
    q.year,
    q.quarter_num,
    q.quarter_end_date,
    m.metric_name,
    m.statement_type,
    f.metric_value
FROM fact_financials f
JOIN dim_bank b ON f.idrssd = b.idrssd
JOIN dim_quarter q ON f.quarter_id = q.quarter_id
JOIN dim_financial_metric m ON f.metric_id = m.metric_id;


-- 2. CRISIS HEATMAP VIEW (Wide Format)
-- Pivots key metrics into columns specifically for Q4 2022
CREATE OR REPLACE VIEW vw_q4_2022_crisis_heatmap AS
SELECT 
    b.bank_name,
    b.ticker,
    MAX(CASE WHEN m.metric_name = 'Uninsured_Deposit_Ratio' THEN f.metric_value END) AS Uninsured_Deposit_Ratio,
    MAX(CASE WHEN m.metric_name = 'Liquidity_Fragility_Ratio' THEN f.metric_value END) AS Liquidity_Fragility_Ratio,
    MAX(CASE WHEN m.metric_name = 'HTM_Concentration_Ratio' THEN f.metric_value END) AS HTM_Concentration,
    MAX(CASE WHEN m.metric_name = 'Unrealized_HTM_Losses' THEN f.metric_value END) AS Unrealized_HTM_Losses
FROM fact_financials f
JOIN dim_bank b ON f.idrssd = b.idrssd
JOIN dim_quarter q ON f.quarter_id = q.quarter_id
JOIN dim_financial_metric m ON f.metric_id = m.metric_id
WHERE q.quarter_id = '2022-Q4'
GROUP BY b.bank_name, b.ticker;


-- 3. MACRO MARKET VIEW
-- Combines the Fed Funds Rate with Bank Stock Prices for the timeline chart
CREATE OR REPLACE VIEW vw_macro_market_timeline AS
SELECT 
    d.date,
    b.bank_name,
    b.ticker,
    mkt.close_price,
    mkt.volume,
    fed.fed_funds_rate
FROM fact_daily_market mkt
JOIN dim_bank b ON mkt.idrssd = b.idrssd
JOIN dim_date d ON mkt.date = d.date
LEFT JOIN dim_macro_fed_rates fed ON d.date = fed.date;
