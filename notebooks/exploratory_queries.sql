SELECT id, company_name
FROM companies
ORDER BY RANDOM()
LIMIT 5;

SELECT
    company_id,
    MIN(year) AS first_year,
    MAX(year) AS last_year,
    COUNT(DISTINCT year) AS total_years
FROM profitandloss
GROUP BY company_id
ORDER BY company_id;

SELECT
    company_id,
    COUNT(DISTINCT year) AS total_years
FROM profitandloss
GROUP BY company_id
HAVING COUNT(DISTINCT year) < 5;


SELECT *
FROM profitandloss
WHERE company_id = 'JIOFIN'
ORDER BY year;

SELECT
    company_id,
    year,
    total_assets,
    total_liabilities
FROM balancesheet
LIMIT 20;

SELECT
    company_id,
    year,
    net_cash_flow
FROM cashflow
LIMIT 20;

SELECT
    company_id,
    date,
    close_price
FROM stock_prices
WHERE close_price <= 0;