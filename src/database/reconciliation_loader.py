from pathlib import Path
import pandas as pd

from src.database.db_connection import get_db_connection


# Project root folder
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Reconciliation CSV path
RECONCILIATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "reports"
    / "reconciliation_results.csv"
)


def load_reconciliation_results():

    print("Starting reconciliation database loader...")

    # Check whether the CSV file exists
    if not RECONCILIATION_FILE.exists():
        raise FileNotFoundError(
            f"File not found: {RECONCILIATION_FILE}"
        )

    # Read reconciliation results
    df = pd.read_csv(RECONCILIATION_FILE)

    print(f"Found {len(df)} reconciliation records.")

    # Convert missing values to None for PostgreSQL
    df = df.astype(object).where(pd.notna(df), None)

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # Create a pipeline run record
            cursor.execute(
                """
                INSERT INTO pipeline_runs (
                    pipeline_name,
                    status,
                    started_at
                )
                VALUES (
                    %s,
                    %s,
                    CURRENT_TIMESTAMP
                )
                RETURNING run_id;
                """,
                (
                    "FinanceMate AI Reconciliation",
                    "RUNNING",
                ),
            )

            run_id = cursor.fetchone()[0]

            print(f"Created pipeline run: {run_id}")

            # Load reconciliation rows
            for _, row in df.iterrows():

                cursor.execute(
                    """
                    INSERT INTO reconciliation_results (
                        run_id,
                        reference_id,
                        company_transaction_id,
                        bank_transaction_id,
                        company_amount,
                        bank_amount,
                        amount_difference,
                        reconciliation_status
                    )
                    VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )

                    ON CONFLICT (reference_id)
                    DO UPDATE SET
                        run_id = EXCLUDED.run_id,
                        company_transaction_id =
                            EXCLUDED.company_transaction_id,
                        bank_transaction_id =
                            EXCLUDED.bank_transaction_id,
                        company_amount =
                            EXCLUDED.company_amount,
                        bank_amount =
                            EXCLUDED.bank_amount,
                        amount_difference =
                            EXCLUDED.amount_difference,
                        reconciliation_status =
                            EXCLUDED.reconciliation_status,
                        created_at = CURRENT_TIMESTAMP;
                    """,
                    (
                        run_id,
                        row["reference_id"],
                        row["company_transaction_id"],
                        row["bank_transaction_id"],
                        row["company_amount"],
                        row["bank_amount"],
                        row["amount_difference"],
                        row["reconciliation_status"],
                    ),
                )

            # Mark pipeline as completed
            cursor.execute(
                """
                UPDATE pipeline_runs
                SET
                    status = %s,
                    completed_at = CURRENT_TIMESTAMP,
                    total_records = %s
                WHERE run_id = %s;
                """,
                (
                    "COMPLETED",
                    len(df),
                    run_id,
                ),
            )

        connection.commit()

        print("Reconciliation loading completed!")
        print(f"Records processed: {len(df)}")
        print(f"Pipeline run ID: {run_id}")

    except Exception as error:

        connection.rollback()

        print("Reconciliation loading failed.")
        print(f"Error: {error}")

        raise

    finally:
        connection.close()


if __name__ == "__main__":
    load_reconciliation_results()