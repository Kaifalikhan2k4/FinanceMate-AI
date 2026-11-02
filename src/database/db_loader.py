
# ============================================================
# FINANCEMATE AI
# FINANCIAL DATABASE LOADER
# Python -> PostgreSQL
# ============================================================

import pandas as pd

from decimal import Decimal
from pathlib import Path

from src.database.db_connection import get_db_connection


# ------------------------------------------------------------
# STEP 1: PROJECT PATH
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_FOLDER = PROJECT_ROOT / "data" / "processed"


# ------------------------------------------------------------
# STEP 2: DATABASE INSERT QUERIES
# ------------------------------------------------------------

SALES_QUERY = """
INSERT INTO sales_transactions (
    transaction_id,
    transaction_date,
    description,
    category,
    department,
    amount,
    payment_mode,
    status,
    reference_id,
    source_row_number,
    source_file
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
ON CONFLICT (transaction_id)
DO UPDATE SET
    transaction_date = EXCLUDED.transaction_date,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    department = EXCLUDED.department,
    amount = EXCLUDED.amount,
    payment_mode = EXCLUDED.payment_mode,
    status = EXCLUDED.status,
    reference_id = EXCLUDED.reference_id,
    source_row_number = EXCLUDED.source_row_number,
    source_file = EXCLUDED.source_file,
    updated_at = CURRENT_TIMESTAMP;
"""


EXPENSE_QUERY = """
INSERT INTO expense_transactions (
    transaction_id,
    transaction_date,
    description,
    category,
    department,
    amount,
    payment_mode,
    status,
    reference_id,
    source_row_number,
    source_file
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
ON CONFLICT (transaction_id)
DO UPDATE SET
    transaction_date = EXCLUDED.transaction_date,
    description = EXCLUDED.description,
    category = EXCLUDED.category,
    department = EXCLUDED.department,
    amount = EXCLUDED.amount,
    payment_mode = EXCLUDED.payment_mode,
    status = EXCLUDED.status,
    reference_id = EXCLUDED.reference_id,
    source_row_number = EXCLUDED.source_row_number,
    source_file = EXCLUDED.source_file,
    updated_at = CURRENT_TIMESTAMP;
"""


BANK_QUERY = """
INSERT INTO bank_transactions (
    bank_transaction_id,
    transaction_date,
    description,
    amount,
    transaction_type,
    reference_id,
    source_row_number,
    source_file
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s
)
ON CONFLICT (bank_transaction_id)
DO UPDATE SET
    transaction_date = EXCLUDED.transaction_date,
    description = EXCLUDED.description,
    amount = EXCLUDED.amount,
    transaction_type = EXCLUDED.transaction_type,
    reference_id = EXCLUDED.reference_id,
    source_row_number = EXCLUDED.source_row_number,
    source_file = EXCLUDED.source_file,
    updated_at = CURRENT_TIMESTAMP;
"""


# ------------------------------------------------------------
# STEP 3: HELPER FUNCTION
# CONVERT EMPTY VALUES INTO NONE
# ------------------------------------------------------------

def clean_value(value):

    if pd.isna(value):
        return None

    return value


# ------------------------------------------------------------
# STEP 4: PREPARE FINANCIAL AMOUNT
# ------------------------------------------------------------

def convert_amount(value):

    if pd.isna(value):
        raise ValueError("Amount cannot be empty.")

    return Decimal(str(value))


# ------------------------------------------------------------
# STEP 5: READ AND CHECK VALIDATED CSV
# ------------------------------------------------------------

def read_validated_file(file_name):

    file_path = PROCESSED_FOLDER / file_name

    if not file_path.is_file():

        raise FileNotFoundError(
            f"Validated file not found: {file_path}. "
            "Run the validation pipeline first."
        )

    df = pd.read_csv(file_path)

    if "validation_status" not in df.columns:

        raise ValueError(
            f"Validation status missing in {file_name}"
        )

    # Only load records that passed validation
    df = df[
        df["validation_status"] == "VALID"
    ].copy()

    return df, file_path.name


# ------------------------------------------------------------
# STEP 6: LOAD SALES TRANSACTIONS
# ------------------------------------------------------------

def load_sales(cursor):

    df, source_file = read_validated_file(
        "sales_validated.csv"
    )

    rows = []

    for record in df.to_dict("records"):

        rows.append((

            record["transaction_id"],

            pd.to_datetime(
                record["date"],
                errors="raise"
            ).date(),

            clean_value(record["description"]),

            clean_value(record["category"]),

            clean_value(record["department"]),

            convert_amount(record["amount"]),

            clean_value(record["payment_mode"]),

            record["status"],

            clean_value(record["reference_id"]),

            int(record["source_row_number"]),

            source_file

        ))

    if rows:
        cursor.executemany(SALES_QUERY, rows)

    print(f"Sales records processed: {len(rows)}")


# ------------------------------------------------------------
# STEP 7: LOAD EXPENSE TRANSACTIONS
# ------------------------------------------------------------

def load_expenses(cursor):

    df, source_file = read_validated_file(
        "expenses_validated.csv"
    )

    rows = []

    for record in df.to_dict("records"):

        rows.append((

            record["transaction_id"],

            pd.to_datetime(
                record["date"],
                errors="raise"
            ).date(),

            clean_value(record["description"]),

            clean_value(record["category"]),

            clean_value(record["department"]),

            convert_amount(record["amount"]),

            clean_value(record["payment_mode"]),

            record["status"],

            clean_value(record["reference_id"]),

            int(record["source_row_number"]),

            source_file

        ))

    if rows:
        cursor.executemany(EXPENSE_QUERY, rows)

    print(f"Expense records processed: {len(rows)}")


# ------------------------------------------------------------
# STEP 8: LOAD BANK TRANSACTIONS
# ------------------------------------------------------------

def load_bank_transactions(cursor):

    df, source_file = read_validated_file(
        "bank_statement_validated.csv"
    )

    rows = []

    for record in df.to_dict("records"):

        rows.append((

            record["bank_transaction_id"],

            pd.to_datetime(
                record["date"],
                errors="raise"
            ).date(),

            clean_value(record["description"]),

            convert_amount(record["amount"]),

            record["transaction_type"],

            clean_value(record["reference_id"]),

            int(record["source_row_number"]),

            source_file

        ))

    if rows:
        cursor.executemany(BANK_QUERY, rows)

    print(f"Bank records processed: {len(rows)}")


# ------------------------------------------------------------
# STEP 9: RUN COMPLETE DATABASE LOADING PIPELINE
# ------------------------------------------------------------

def run_database_loader():

    print("\n======================================")

    print("FINANCEMATE AI DATABASE LOADER STARTED")

    print("======================================")

    # Establish PostgreSQL connection
    # One transaction covers all three datasets.

    with get_db_connection() as connection:

        with connection.cursor() as cursor:

            load_sales(cursor)

            load_expenses(cursor)

            load_bank_transactions(cursor)

    # The connection context commits if successful.
    # If an operation fails, the transaction rolls back.

    print("\n======================================")

    print("DATABASE LOADING COMPLETED")

    print("======================================")


# ------------------------------------------------------------
# STEP 10: PROGRAM ENTRY POINT
# ------------------------------------------------------------

if __name__ == "__main__":

    run_database_loader()
