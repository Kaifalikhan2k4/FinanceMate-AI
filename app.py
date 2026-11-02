"""
FinanceMate AI - Streamlit Chatbot
"""

import streamlit as st
import pandas as pd

from decimal import Decimal
from datetime import date, datetime

from src.assistant.query_handler import handle_question


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="FinanceMate AI",
    page_icon="💰",
    layout="wide",
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_currency(value):
    """Format a number as Indian Rupees."""

    if value is None:
        value = 0

    return f"₹{float(value):,.2f}"


def convert_for_display(value):
    """Convert database values into display-friendly values."""

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (date, datetime)):
        return value.strftime("%d-%b-%Y")

    return value


def display_result(result):

    result_type = result.get("type")
    data = result.get("data")

    # Financial summary
    if result_type == "financial_summary":

        st.subheader("Financial Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Revenue",
            format_currency(data["total_revenue"]),
        )

        col2.metric(
            "Total Expenses",
            format_currency(data["total_expenses"]),
        )

        col3.metric(
            "Net Profit",
            format_currency(data["net_profit"]),
        )

    # Department expenses
    elif result_type == "department_expenses":

        st.subheader("Department-wise Expenses")

        df = pd.DataFrame(data)

        if not df.empty:
            st.dataframe(df, use_container_width=True)

            st.bar_chart(
                df.set_index("department")["total_expenses"]
            )

    # Top expenses
    elif result_type == "top_expenses":

        st.subheader("Top Expenses")

        df = pd.DataFrame(data)

        if not df.empty:
            st.dataframe(df, use_container_width=True)

    # Reconciliation summary
    elif result_type == "reconciliation_summary":

        st.subheader("Reconciliation Summary")

        df = pd.DataFrame(data)

        if not df.empty:
            st.dataframe(df, use_container_width=True)

    # Reconciliation issues
    elif result_type == "reconciliation_issues":

        st.subheader("Reconciliation Issues")

        df = pd.DataFrame(data)

        if not df.empty:
            st.dataframe(df, use_container_width=True)

        else:
            st.success("No reconciliation issues found.")

    # Monthly financial summary
    elif result_type == "monthly_financial_summary":

        st.subheader("Monthly Financial Summary")

        df = pd.DataFrame(data)

        if not df.empty:

            df["month"] = pd.to_datetime(df["month"])

            st.dataframe(df, use_container_width=True)

            chart_df = df.set_index("month")[
                ["revenue", "expenses", "net_profit"]
            ]

            st.line_chart(chart_df)

    # Category expenses
    elif result_type == "category_expenses":

        st.subheader("Category-wise Expenses")

        df = pd.DataFrame(data)

        if not df.empty:
            st.dataframe(df, use_container_width=True)

            st.bar_chart(
                df.set_index("category")["total_expenses"]
            )

    # Unknown question
    elif result_type == "unknown":

        st.warning(result.get("message"))


# ============================================================
# MAIN INTERFACE
# ============================================================

st.title("💰 FinanceMate AI")

st.markdown(
    """
    ### Financial Intelligence & Audit Automation

    Ask questions about revenue, expenses, profit,
    departments, or bank reconciliation.
    """
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("FinanceMate AI")

    st.markdown("### Example Questions")

    st.markdown(
        """
        - What is our total revenue and profit?
        - Which department spends the most?
        - Show me the top expenses
        - Show monthly financial summary
        - Show category-wise expenses
        - Find bank discrepancies
        - Show reconciliation summary
        """
    )

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# ============================================================
# CHAT HISTORY
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        if message["role"] == "user":
            st.markdown(message["content"])

        else:
            st.markdown(message["content"])

            if "result" in message:
                display_result(message["result"])


# ============================================================
# USER INPUT
# ============================================================

question = st.chat_input(
    "Ask FinanceMate AI a financial question..."
)


if question:

    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Process question
    with st.chat_message("assistant"):

        try:

            result = handle_question(question)

            if result["type"] == "unknown":

                answer = result["message"]

                st.warning(answer)

            else:

                answer = (
                    "I retrieved the requested financial information "
                    "from the FinanceMate AI database."
                )

                st.markdown(answer)

                display_result(result)

            # Save assistant response
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "result": result,
                }
            )

        except Exception as error:

            st.error(
                "Something went wrong while processing your question."
            )

            st.exception(error)