"""
FinanceMate AI - Rule-Based Query Handler
"""

from src.assistant.financial_service import (
    get_financial_summary,
    get_department_expenses,
    get_top_expenses,
    get_reconciliation_summary,
    get_reconciliation_issues,
    get_monthly_financial_summary,
    get_category_expenses,
)


def handle_question(question):

    question = question.lower().strip()

    # 1. Top / highest expenses
    if any(word in question for word in [
        "top expense",
        "top expenses",
        "highest expense",
        "highest expenses",
        "largest expense",
        "largest expenses",
        "most expensive",
    ]):
        return {
            "type": "top_expenses",
            "data": get_top_expenses(),
        }

    # 2. Reconciliation summary
    elif any(word in question for word in [
        "reconciliation summary",
        "reconciliation status",
        "matched transactions",
        "reconciliation overview",
    ]):
        return {
            "type": "reconciliation_summary",
            "data": get_reconciliation_summary(),
        }

    # 3. Reconciliation issues
    elif any(word in question for word in [
        "discrepancy",
        "discrepancies",
        "unmatched",
        "reconciliation issue",
        "bank mismatch",
        "bank difference",
    ]):
        return {
            "type": "reconciliation_issues",
            "data": get_reconciliation_issues(),
        }

    # 4. Department expenses
    elif any(word in question for word in [
        "department",
        "department-wise",
        "department wise",
    ]):
        return {
            "type": "department_expenses",
            "data": get_department_expenses(),
        }

    # 5. Monthly financial analysis
    elif any(word in question for word in [
        "monthly",
        "month-wise",
        "month wise",
    ]):
        return {
            "type": "monthly_financial_summary",
            "data": get_monthly_financial_summary(),
        }

    # 6. Category expenses
    elif any(word in question for word in [
        "category",
        "category-wise",
        "category wise",
    ]):
        return {
            "type": "category_expenses",
            "data": get_category_expenses(),
        }

    # 7. Financial summary
    elif any(word in question for word in [
        "revenue",
        "profit",
        "net income",
        "financial summary",
        "financial overview",
        "total expenses",
        "how much did we earn",
    ]):
        return {
            "type": "financial_summary",
            "data": get_financial_summary(),
        }

    # 8. Unknown question
    else:
        return {
            "type": "unknown",
            "message": (
                "I couldn't understand your question. "
                "Try asking about revenue, profit, expenses, "
                "departments, monthly analysis, or reconciliation."
            ),
        }