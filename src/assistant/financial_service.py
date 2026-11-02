"""
FinanceMate AI - Financial Analytics Service

This module retrieves financial information from PostgreSQL.
It contains read-only analytics functions.
"""

from src.database.db_connection import get_db_connection


# ============================================================
# 1. GENERIC DATABASE FUNCTIONS
# ============================================================

def fetch_all(query, params=None):
    """
    Execute a SQL query and return all rows as dictionaries.
    """

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())

            # Get the names of the returned columns
            column_names = [
                column.name for column in cursor.description
            ]

            # Fetch all records
            rows = cursor.fetchall()

            # Convert rows into dictionaries
            results = []

            for row in rows:
                record = dict(zip(column_names, row))
                results.append(record)

            return results

    finally:
        connection.close()


def fetch_one(query, params=None):
    """
    Execute a query and return the first row as a dictionary.
    """

    results = fetch_all(query, params)

    if results:
        return results[0]

    return {}


# ============================================================
# 2. FINANCIAL SUMMARY
# ============================================================

def get_financial_summary():
    """
    Calculate total revenue, total expenses, and net profit.
    """

    query = """
        SELECT
            COALESCE(
                (
                    SELECT SUM(amount)
                    FROM sales_transactions
                    WHERE LOWER(status) = 'completed'
                ),
                0
            ) AS total_revenue,

            COALESCE(
                (
                    SELECT SUM(amount)
                    FROM expense_transactions
                    WHERE LOWER(status) = 'completed'
                ),
                0
            ) AS total_expenses,

            COALESCE(
                (
                    SELECT SUM(amount)
                    FROM sales_transactions
                    WHERE LOWER(status) = 'completed'
                ),
                0
            )
            -
            COALESCE(
                (
                    SELECT SUM(amount)
                    FROM expense_transactions
                    WHERE LOWER(status) = 'completed'
                ),
                0
            ) AS net_profit;
    """

    return fetch_one(query)


# ============================================================
# 3. DEPARTMENT-WISE EXPENSES
# ============================================================

def get_department_expenses():
    """
    Calculate total expenses for each department.
    """

    query = """
        SELECT
            department,
            COUNT(*) AS transaction_count,
            SUM(amount) AS total_expenses

        FROM expense_transactions

        WHERE LOWER(status) = 'completed'

        GROUP BY department

        ORDER BY total_expenses DESC;
    """

    return fetch_all(query)


# ============================================================
# 4. TOP EXPENSE TRANSACTIONS
# ============================================================

def get_top_expenses(limit=5):
    """
    Retrieve the highest expense transactions.

    Parameters:
        limit: Number of transactions to retrieve.
    """

    # Prevent invalid limits
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("Limit must be a positive integer.")

    query = """
        SELECT
            transaction_id,
            transaction_date,
            description,
            department,
            amount

        FROM expense_transactions

        WHERE LOWER(status) = 'completed'

        ORDER BY amount DESC

        LIMIT %s;
    """

    return fetch_all(query, (limit,))


# ============================================================
# 5. RECONCILIATION SUMMARY
# ============================================================

def get_reconciliation_summary():
    """
    Count reconciliation records by status.
    """

    query = """
        SELECT
            reconciliation_status,
            COUNT(*) AS record_count

        FROM reconciliation_results

        GROUP BY reconciliation_status

        ORDER BY record_count DESC;
    """

    return fetch_all(query)


# ============================================================
# 6. RECONCILIATION ISSUES
# ============================================================

def get_reconciliation_issues():
    """
    Retrieve discrepancies and unmatched transactions.
    """

    query = """
        SELECT
            reference_id,
            company_transaction_id,
            bank_transaction_id,
            company_amount,
            bank_amount,
            amount_difference,
            reconciliation_status

        FROM reconciliation_results

        WHERE LOWER(reconciliation_status) <> 'matched'

        ORDER BY reference_id;
    """

    return fetch_all(query)


# ============================================================
# 7. MONTHLY FINANCIAL SUMMARY
# ============================================================

def get_monthly_financial_summary():
    """
    Retrieve monthly revenue, expenses, and net profit.
    """

    query = """
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
            ON r.month = e.month

        ORDER BY month;
    """

    return fetch_all(query)


# ============================================================
# 8. CATEGORY-WISE EXPENSES
# ============================================================

def get_category_expenses():
    """
    Calculate total expenses by category.
    """

    query = """
        SELECT
            category,
            COUNT(*) AS transaction_count,
            SUM(amount) AS total_expenses

        FROM expense_transactions

        WHERE LOWER(status) = 'completed'

        GROUP BY category

        ORDER BY total_expenses DESC;
    """

    return fetch_all(query)