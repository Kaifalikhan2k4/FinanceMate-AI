
-- ============================================================
-- FINANCEMATE AI
-- FINANCIAL ANALYTICS ENGINE
-- ============================================================


-- ============================================================
-- QUERY 1: TOTAL REVENUE
-- ============================================================

SELECT
    COALESCE(SUM(amount), 0) AS total_revenue
FROM sales_transactions
WHERE LOWER(status) = 'completed';


-- ============================================================
-- QUERY 2: TOTAL EXPENSES
-- ============================================================

SELECT
    COALESCE(SUM(amount), 0) AS total_expenses
FROM expense_transactions
WHERE LOWER(status) = 'completed';


-- ============================================================
-- QUERY 3: NET PROFIT
-- ============================================================

SELECT
    COALESCE(
        (SELECT SUM(amount)
         FROM sales_transactions
         WHERE LOWER(status) = 'completed'),
        0
    )
    -
    COALESCE(
        (SELECT SUM(amount)
         FROM expense_transactions
         WHERE LOWER(status) = 'completed'),
        0
    ) AS net_profit;


-- ============================================================
-- QUERY 4: REVENUE AND EXPENSE SUMMARY
-- ============================================================

SELECT
    (SELECT COALESCE(SUM(amount), 0)
     FROM sales_transactions
     WHERE LOWER(status) = 'completed') AS revenue,

    (SELECT COALESCE(SUM(amount), 0)
     FROM expense_transactions
     WHERE LOWER(status) = 'completed') AS expenses,

    (SELECT COALESCE(SUM(amount), 0)
     FROM sales_transactions
     WHERE LOWER(status) = 'completed')
    -
    (SELECT COALESCE(SUM(amount), 0)
     FROM expense_transactions
     WHERE LOWER(status) = 'completed') AS net_profit;


-- ============================================================
-- QUERY 5: DEPARTMENT-WISE EXPENSE ANALYSIS
-- ============================================================

SELECT
    department,
    COUNT(*) AS total_transactions,
    SUM(amount) AS total_expenses,
    ROUND(AVG(amount), 2) AS average_expense

FROM expense_transactions

WHERE LOWER(status) = 'completed'

GROUP BY department

ORDER BY total_expenses DESC;


-- ============================================================
-- QUERY 6: CATEGORY-WISE EXPENSE ANALYSIS
-- ============================================================

SELECT
    category,
    COUNT(*) AS total_transactions,
    SUM(amount) AS total_expenses

FROM expense_transactions

WHERE LOWER(status) = 'completed'

GROUP BY category

ORDER BY total_expenses DESC;


-- ============================================================
-- QUERY 7: MONTHLY REVENUE
-- ============================================================

SELECT
    DATE_TRUNC('month', transaction_date)::DATE AS month,

    SUM(amount) AS monthly_revenue

FROM sales_transactions

WHERE LOWER(status) = 'completed'

GROUP BY DATE_TRUNC('month', transaction_date)

ORDER BY month;


-- ============================================================
-- QUERY 8: MONTHLY EXPENSES
-- ============================================================

SELECT
    DATE_TRUNC('month', transaction_date)::DATE AS month,

    SUM(amount) AS monthly_expenses

FROM expense_transactions

WHERE LOWER(status) = 'completed'

GROUP BY DATE_TRUNC('month', transaction_date)

ORDER BY month;


-- ============================================================
-- QUERY 9: PENDING AND FAILED TRANSACTIONS
-- ============================================================

SELECT
    status,
    COUNT(*) AS total_transactions,
    SUM(amount) AS total_amount

FROM (

    SELECT status, amount
    FROM sales_transactions

    UNION ALL

    SELECT status, amount
    FROM expense_transactions

) AS all_transactions

GROUP BY status

ORDER BY status;


-- ============================================================
-- QUERY 10: TOP 5 HIGHEST EXPENSE TRANSACTIONS
-- ============================================================

SELECT
    transaction_id,
    description,
    department,
    amount,
    transaction_date

FROM expense_transactions

WHERE LOWER(status) = 'completed'

ORDER BY amount DESC

LIMIT 5;


-- ============================================================
-- QUERY 11: BANK CREDIT AND DEBIT ANALYSIS
-- ============================================================

SELECT
    transaction_type,

    COUNT(*) AS total_transactions,

    SUM(amount) AS total_amount

FROM bank_transactions

GROUP BY transaction_type

ORDER BY transaction_type;


-- ============================================================
-- QUERY 12: CREATE FINANCIAL OVERVIEW VIEW
-- ============================================================

CREATE OR REPLACE VIEW v_financial_overview AS

SELECT

    COALESCE(
        (SELECT SUM(amount)
         FROM sales_transactions
         WHERE LOWER(status) = 'completed'),
        0
    ) AS total_revenue,

    COALESCE(
        (SELECT SUM(amount)
         FROM expense_transactions
         WHERE LOWER(status) = 'completed'),
        0
    ) AS total_expenses,

    COALESCE(
        (SELECT SUM(amount)
         FROM sales_transactions
         WHERE LOWER(status) = 'completed'),
        0
    )
    -
    COALESCE(
        (SELECT SUM(amount)
         FROM expense_transactions
         WHERE LOWER(status) = 'completed'),
        0
    ) AS net_profit;


-- ============================================================
-- QUERY 13: CREATE MONTHLY FINANCIAL SUMMARY VIEW
-- ============================================================

CREATE OR REPLACE VIEW v_monthly_financial_summary AS

WITH monthly_revenue AS (

    SELECT
        DATE_TRUNC('month', transaction_date)::DATE AS month,
        SUM(amount) AS revenue

    FROM sales_transactions

    WHERE LOWER(status) = 'completed'

    GROUP BY DATE_TRUNC('month', transaction_date)

),

monthly_expenses AS (

    SELECT
        DATE_TRUNC('month', transaction_date)::DATE AS month,
        SUM(amount) AS expenses

    FROM expense_transactions

    WHERE LOWER(status) = 'completed'

    GROUP BY DATE_TRUNC('month', transaction_date)

)

SELECT

    COALESCE(r.month, e.month) AS month,

    COALESCE(r.revenue, 0) AS revenue,

    COALESCE(e.expenses, 0) AS expenses,

    COALESCE(r.revenue, 0)
    -
    COALESCE(e.expenses, 0) AS net_profit

FROM monthly_revenue r

FULL OUTER JOIN monthly_expenses e

ON r.month = e.month;


-- ============================================================
-- QUERY 14: CREATE DEPARTMENT EXPENSE VIEW
-- ============================================================

CREATE OR REPLACE VIEW v_department_expenses AS

SELECT

    department,

    COUNT(*) AS transaction_count,

    SUM(amount) AS total_expenses,

    ROUND(AVG(amount), 2) AS average_expense

FROM expense_transactions

WHERE LOWER(status) = 'completed'

GROUP BY department;


-- ============================================================
-- QUERY 15: CREATE CATEGORY EXPENSE VIEW
-- ============================================================

CREATE OR REPLACE VIEW v_category_expenses AS

SELECT

    category,

    COUNT(*) AS transaction_count,

    SUM(amount) AS total_expenses

FROM expense_transactions

WHERE LOWER(status) = 'completed'

GROUP BY category;


-- ============================================================
-- FINANCEMATE AI ANALYTICS ENGINE COMPLETED
-- ============================================================
