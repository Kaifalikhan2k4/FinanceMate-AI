
# ============================================================
# FINANCEMATE AI
# FINANCIAL DATA CLEANING AND VALIDATION ENGINE
# ============================================================

import pandas as pd
import json

from pathlib import Path
from src.ingestion.file_reader import load_financial_files


# ------------------------------------------------------------
# STEP 1: DEFINE PROJECT FOLDERS
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_FOLDER = PROJECT_ROOT / "data" / "processed"
REPORTS_FOLDER = PROJECT_ROOT / "data" / "reports"

PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
REPORTS_FOLDER.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# STEP 2: DEFINE REQUIRED COLUMNS
# ------------------------------------------------------------

REQUIRED_FIELDS = {

    "sales": [
        "transaction_id",
        "date",
        "description",
        "category",
        "department",
        "amount",
        "payment_mode",
        "status",
        "reference_id"
    ],

    "expenses": [
        "transaction_id",
        "date",
        "description",
        "category",
        "department",
        "amount",
        "payment_mode",
        "status",
        "reference_id"
    ],

    "bank_statement": [
        "bank_transaction_id",
        "date",
        "description",
        "amount",
        "transaction_type",
        "reference_id"
    ]
}


# ------------------------------------------------------------
# STEP 3: DEFINE TRANSACTION ID COLUMNS
# ------------------------------------------------------------

ID_COLUMNS = {
    "sales": "transaction_id",
    "expenses": "transaction_id",
    "bank_statement": "bank_transaction_id"
}


# ------------------------------------------------------------
# STEP 4: DATA CLEANING FUNCTION
# ------------------------------------------------------------

def clean_dataframe(df, dataset_name):

    print(f"\nCleaning {dataset_name} data...")

    # Create a separate copy.
    # Never modify the original uploaded dataset.

    df = df.copy()

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    # Check required columns
    required = REQUIRED_FIELDS[dataset_name]

    missing_columns = [
        column for column in required
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Keep original values for audit investigation
    df["_original_date"] = df["date"].copy()
    df["_original_amount"] = df["amount"].copy()

    # Add original Excel row numbers.
    # Row 1 is assumed to contain the column headers.
    df["source_row_number"] = range(2, len(df) + 2)

    # --------------------------------------------------------
    # STEP 4A: CLEAN TEXT FORMATS
    # --------------------------------------------------------

    text_columns = df.select_dtypes(
        include=["object", "str"]
    ).columns

    for column in text_columns:

        df[column] = df[column].str.strip()

        # Convert empty strings into missing values
        df[column] = df[column].replace("", pd.NA)

    # --------------------------------------------------------
    # STEP 4B: CONVERT DATE COLUMN
    # --------------------------------------------------------

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # STEP 4C: CONVERT AMOUNT INTO NUMERIC FORMAT
    # --------------------------------------------------------

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # STEP 5: IDENTIFY DATA QUALITY ISSUES
    # --------------------------------------------------------

    # Store all issues associated with each record
    issues = [[] for _ in range(len(df))]

    def add_issue(mask, message):

        for position, has_issue in enumerate(mask.tolist()):

            if has_issue:
                issues[position].append(message)

    # 5A. Missing required values

    for column in required:

        missing_mask = df[column].isna()

        add_issue(
            missing_mask,
            f"Missing required value: {column}"
        )

    # 5B. Invalid dates

    invalid_date_mask = (
        df["_original_date"].notna()
        & df["date"].isna()
    )

    add_issue(
        invalid_date_mask,
        "Invalid date format"
    )

    # 5C. Invalid amounts

    invalid_amount_mask = (
        df["_original_amount"].notna()
        & df["amount"].isna()
    )

    add_issue(
        invalid_amount_mask,
        "Amount is not numeric"
    )

    # 5D. Negative amounts

    negative_amount_mask = df["amount"] < 0

    add_issue(
        negative_amount_mask,
        "Negative transaction amount"
    )

    # 5E. Duplicate transaction IDs

    id_column = ID_COLUMNS[dataset_name]

    duplicate_id_mask = (
        df[id_column].notna()
        & df[id_column].duplicated(keep="first")
    )

    add_issue(
        duplicate_id_mask,
        "Duplicate transaction ID"
    )

    # --------------------------------------------------------
    # STEP 6: SEPARATE VALID AND INVALID RECORDS
    # --------------------------------------------------------

    df["issue_reasons"] = [
        "; ".join(record_issues)
        for record_issues in issues
    ]

    # Records without any issue are accepted
    accepted_df = df[
        df["issue_reasons"] == ""
    ].copy()

    # Records with one or more issues are rejected
    rejected_df = df[
        df["issue_reasons"] != ""
    ].copy()

    # Remove temporary audit columns from accepted data.
    # Keep original values in rejected records for investigation.

    accepted_df = accepted_df.drop(
        columns=["_original_date", "_original_amount",
                 "issue_reasons"]
    )

    rejected_df = rejected_df.rename(
        columns={
            "_original_date": "original_date",
            "_original_amount": "original_amount"
        }
    )

    # --------------------------------------------------------
    # STEP 7: GENERATE CLEANING SUMMARY
    # --------------------------------------------------------

    issue_counts = {}

    for record_issues in issues:

        for issue in record_issues:

            issue_counts[issue] = (
                issue_counts.get(issue, 0) + 1
            )

    summary = {

        "dataset": dataset_name,

        "total_records": len(df),

        "accepted_records": len(accepted_df),

        "rejected_records": len(rejected_df),

        "issue_counts": issue_counts
    }

    print("\nCleaning completed!")

    print("Total records:", len(df))
    print("Accepted records:", len(accepted_df))
    print("Rejected records:", len(rejected_df))

    print("Data quality issues:", issue_counts)

    return accepted_df, rejected_df, summary


# ------------------------------------------------------------
# STEP 8: SAVE PROCESSED DATA AND REPORTS
# ------------------------------------------------------------

def save_cleaning_results(
    accepted_df,
    rejected_df,
    summary,
    dataset_name
):

    # Save valid records
    clean_file = (
        PROCESSED_FOLDER
        / f"{dataset_name}_cleaned.csv"
    )

    accepted_df.to_csv(
        clean_file,
        index=False
    )

    # Save records that require investigation
    rejected_file = (
        REPORTS_FOLDER
        / f"{dataset_name}_rejected.csv"
    )

    rejected_df.to_csv(
        rejected_file,
        index=False
    )

    # Save summary report
    summary_file = (
        REPORTS_FOLDER
        / f"{dataset_name}_summary.json"
    )

    with open(summary_file, "w", encoding="utf-8") as file:

        json.dump(
            summary,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nFiles generated:")

    print(clean_file)
    print(rejected_file)
    print(summary_file)


# ------------------------------------------------------------
# STEP 9: MAIN FINANCIAL CLEANING PIPELINE
# ------------------------------------------------------------

def run_cleaning_pipeline():

    print("\n======================================")
    print("FINANCEMATE AI DATA CLEANING STARTED")
    print("======================================")

    # Load original Excel datasets
    sales_df, expenses_df, bank_df = (
        load_financial_files()
    )

    # Store datasets with their names
    datasets = {

        "sales": sales_df,

        "expenses": expenses_df,

        "bank_statement": bank_df

    }

    # Process every dataset
    for dataset_name, dataframe in datasets.items():

        accepted, rejected, summary = clean_dataframe(
            dataframe,
            dataset_name
        )

        save_cleaning_results(
            accepted,
            rejected,
            summary,
            dataset_name
        )

    print("\n======================================")
    print("FINANCEMATE AI CLEANING COMPLETED")
    print("======================================")


# ------------------------------------------------------------
# STEP 10: EXECUTE PROGRAM
# ------------------------------------------------------------

if __name__ == "__main__":

    run_cleaning_pipeline()
