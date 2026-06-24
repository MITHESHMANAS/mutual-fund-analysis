-- 1 Top 5 fund houses by AUM

SELECT fund_house,
       SUM(aum_crore) AS total_aum
FROM aum_by_fund_house
GROUP BY fund_house
ORDER BY total_aum DESC
LIMIT 5;

-- 2 Average NAV

SELECT AVG(nav) AS avg_nav
FROM nav_history;

-- 3 Highest NAV funds

SELECT amfi_code,
       MAX(nav) AS highest_nav
FROM nav_history
GROUP BY amfi_code
ORDER BY highest_nav DESC
LIMIT 10;

-- 4 SIP inflow trend

SELECT month,
       sip_inflow_crore
FROM monthly_sip_inflows
ORDER BY month;

-- 5 Category inflows

SELECT category,
       SUM(net_inflow_crore)
FROM category_inflows
GROUP BY category;

-- 6 Transactions by state

SELECT state,
       COUNT(*) AS transactions
FROM investor_transactions
GROUP BY state
ORDER BY transactions DESC;

-- 7 Transaction amount by type

SELECT transaction_type,
       SUM(amount_inr)
FROM investor_transactions
GROUP BY transaction_type;

-- 8 Expense ratio below 1%

SELECT scheme_name,
       expense_ratio_pct
FROM scheme_performance
WHERE expense_ratio_pct < 1;

-- 9 Top schemes by 5Y return

SELECT scheme_name,
       return_5yr_pct
FROM scheme_performance
ORDER BY return_5yr_pct DESC
LIMIT 10;

-- 10 Sector allocation

SELECT sector,
       AVG(weight_pct)
FROM portfolio_holdings
GROUP BY sector
ORDER BY AVG(weight_pct) DESC;