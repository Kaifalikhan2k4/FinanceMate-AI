
# ======================================================
# FINANCEMATE AI - POSTGRESQL CONNECTION
# ======================================================

import os
import psycopg

from pathlib import Path
from dotenv import load_dotenv


# STEP 1: Find the main project folder

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# STEP 2: Load database settings from .env

load_dotenv(PROJECT_ROOT / ".env")


# STEP 3: Create a reusable database connection function

def get_db_connection():

    # Read database configuration
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    # Check that important settings exist
    if not all([database, username, password]):
        raise ValueError(
            "Missing database credentials. Check your .env file."
        )

    # Establish connection to PostgreSQL
    connection = psycopg.connect(
        host=host,
        port=port,
        dbname=database,
        user=username,
        password=password,
        connect_timeout=10
    )

    return connection


# STEP 4: Test the database connection

def test_connection():

    try:

        # Open connection and automatically close it
        with get_db_connection() as connection:

            with connection.cursor() as cursor:

                # Ask PostgreSQL which database we are using
                cursor.execute(
                    "SELECT current_database(), current_user;"
                )

                result = cursor.fetchone()

                print("\nDATABASE CONNECTION SUCCESSFUL!")

                print("Database:", result[0])
                print("Connected user:", result[1])

                # Check whether our tables exist
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name IN (
                        'sales_transactions',
                        'expense_transactions',
                        'bank_transactions',
                        'reconciliation_results',
                        'pipeline_runs'
                    );
                """)

                table_count = cursor.fetchone()[0]

                print("FinanceMate tables found:", table_count)

                if table_count != 5:
                    print("WARNING: Some tables are missing!")

    except Exception as error:

        print("\nDATABASE CONNECTION FAILED!")

        print("Error:", error)

        raise


# STEP 5: Run only when this file is executed directly

if __name__ == "__main__":

    test_connection()
