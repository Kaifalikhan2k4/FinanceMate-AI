
# ============================================================
# FINANCEMATE AI
# FINANCIAL DATA VALIDATION ENGINE
# ============================================================

import pandas as pd
import json

from pathlib import Path


# ------------------------------------------------------------
# STEP 1: PROJECT FOLDER LOCATIONS
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_FOLDER = PROJECT_ROOT / "data" / "processed"
REPORTS_FOLDER = PROJECT_ROOT / "data" / "reports"

PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
REPORTS_FOLDER.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# STEP 2: DEFINE VALIDATION RULES
# ------------------------------------------------------------

VALID_PAYMENT_MODES = [
    "UPI",
    "Cash",
    "Card",
    "Bank Transfer",
    "Cheque"
]

VALID_STATUSES = [
    "Completed",
    "Pending",
    "Failed"
]

VALID_CATEGORIES = [
    "Sales",
    "Expense"
]

VALID_TRANSACTION_TYPES = [
    "Credit",
    "Debit"
]


# ------------------------------------------------------------
# STEP 3: DEFINE DATASET CONFIGURATION
# ------------------------------------------------------------

DATASET_CONFIG = {

    "sales": {
        "file": "sales_cleaned.csv",
        "id_column": "transaction_id",
        "required_columns": [
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
        "type": "company"
    },

    "expenses": {
        "file": "expenses_cleaned.csv",
        "id_column": "transaction_id",
        "required_columns": [
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
        "type": "company"
    },

    "bank_statement": {
        "file": "bank_statement_cleaned.csv",
        "id_column": "bank_transaction_id",
        "required_columns": [
            "bank_transaction_id",
            "date",
            "description",
            "amount",
            "transaction_type",
            "reference_id"
        ],
        "type": "bank"
    }
}


# ------------------------------------------------------------
# STEP 4: MAIN VALIDATION FUNCTION
# ------------------------------------------------------------

def validate_dataframe(df, dataset_name):

    print(f"\nValidating {dataset_name}...")

    # Work on a separate copy
    df = df.copy()

    # Get configuration for the current dataset
    config = DATASET_CONFIG[dataset_name]

    # Check whether all expected columns exist
    required_columns = config["required_columns"]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in {dataset_name}: "
            f"{missing_columns}"
        )

    # --------------------------------------------------------
    # STEP 5: NORMALIZE IMPORTANT TEXT VALUES
    # --------------------------------------------------------

    if config["type"] == "company":

        for column in ["category", "status"]:

            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
                .str.title()
            )

        df["payment_mode"] = (
            df["payment_mode"]
            .astype("string")
            .str.strip()
        )

    else:

        df["transaction_type"] = (
            df["transaction_type"]
            .astype("string")
            .str.strip()
            .str.title()
        )

    # --------------------------------------------------------
    # STEP 6: CONVERT DATE AND AMOUNT
    # --------------------------------------------------------

    original_date = df["date"].copy()
    original_amount = df["amount"].copy()

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # STEP 7: PREPARE ISSUE LIST
    # --------------------------------------------------------

    issues = [[] for _ in range(len(df))]

    def add_issue(mask, message):

        mask = mask.fillna(False)

        for position, has_issue in enumerate(mask.tolist()):

            if has_issue:
                issues[position].append(message)

    # --------------------------------------------------------
    # STEP 8: CHECK REQUIRED FIELDS
    # --------------------------------------------------------

    for column in required_columns:

        missing_mask = (
            df[column].isna()
            |
            df[column]
            .astype("string")
            .str.strip()
            .eq("")
        )

        add_issue(
            missing_mask,
            f"Required field is missing: {column}"
        )

    # --------------------------------------------------------
    # STEP 9: CHECK TRANSACTION ID UNIQUENESS
    # --------------------------------------------------------

    id_column = config["id_column"]

    duplicate_mask = (
        df[id_column].notna()
        &
        df[id_column].duplicated(keep=False)
    )

    add_issue(
        duplicate_mask,
        "Duplicate transaction ID"
    )

    # --------------------------------------------------------
    # STEP 10: CHECK DATE FORMAT
    # --------------------------------------------------------

    invalid_date_mask = (
        original_date.notna()
        &
        df["date"].isna()
    )

    add_issue(
        invalid_date_mask,
        "Invalid transaction date"
    )

    # --------------------------------------------------------
    # STEP 11: CHECK AMOUNT
    # --------------------------------------------------------

    invalid_amount_mask = (
        original_amount.notna()
        &
        df["amount"].isna()
    )

    add_issue(
        invalid_amount_mask,
        "Amount must be numeric"
    )

    non_positive_amount_mask = df["amount"] <= 0

    add_issue(
        non_positive_amount_mask,
        "Transaction amount must be greater than zero"
    )

    # --------------------------------------------------------
    # STEP 12: COMPANY TRANSACTION VALIDATION
    # --------------------------------------------------------

    if config["type"] == "company":

        invalid_status_mask = ~df["status"].isin(
            VALID_STATUSES
        )

        add_issue(
            invalid_status_mask,
            "Invalid transaction status"
        )

        invalid_payment_mask = ~df["payment_mode"].isin(
            VALID_PAYMENT_MODES
        )

        add_issue(
            invalid_payment_mask,
            "Invalid payment mode"
        )

        invalid_category_mask = ~df["category"].isin(
            VALID_CATEGORIES
        )

        add_issue(
            invalid_category_mask,
            "Invalid transaction category"
        )

    # --------------------------------------------------------
    # STEP 13: BANK TRANSACTION VALIDATION
    # --------------------------------------------------------

    else:

        invalid_type_mask = ~df["transaction_type"].isin(
            VALID_TRANSACTION_TYPES
        )

        add_issue(
            invalid_type_mask,
            "Invalid bank transaction type"
        )

    # --------------------------------------------------------
    # STEP 14: ADD VALIDATION RESULTS
    # --------------------------------------------------------

    df["validation_issues"] = [
        "; ".join(record_issues)
        for record_issues in issues
    ]

    df["validation_status"] = [
        "VALID" if len(record_issues) == 0
        else "REVIEW_REQUIRED"
        for record_issues in issues
    ]

    # --------------------------------------------------------
    # STEP 15: CREATE SUMMARY
    # --------------------------------------------------------

    issue_counts = {}

    for record_issues in issues:

        for issue in record_issues:

            issue_counts[issue] = (
                issue_counts.get(issue, 0) + 1
            )

    valid_count = (
        df["validation_status"] == "VALID"
    ).sum()

    flagged_count = (
        df["validation_status"] == "REVIEW_REQUIRED"
    ).sum()

    summary = {

        "dataset": dataset_name,

        "total_records": len(df),

        "valid_records": int(valid_count),

        "flagged_records": int(flagged_count),

        "issue_counts": issue_counts

    }

    print("Validation completed!")

    print("Total records:", len(df))

    print("Valid records:", valid_count)

    print("Flagged records:", flagged_count)

    print("Validation issues:", issue_counts)

    return df, summary


# ------------------------------------------------------------
# STEP 16: SAVE VALIDATION OUTPUTS
# ------------------------------------------------------------

def save_validation_results(
    validated_df,
    summary,
    dataset_name
):

    # Save all records with validation status
    validated_file = (
        PROCESSED_FOLDER
        / f"{dataset_name}_validated.csv"
    )

    validated_df.to_csv(
        validated_file,
        index=False
    )

    # Save only records requiring review
    flagged_df = validated_df[
        validated_df["validation_status"] == "REVIEW_REQUIRED"
    ].copy()

    flagged_file = (
        REPORTS_FOLDER
        / f"{dataset_name}_validation_issues.csv"
    )

    flagged_df.to_csv(
        flagged_file,
        index=False
    )

    # Save validation summary
    summary_file = (
        REPORTS_FOLDER
        / f"{dataset_name}_validation_summary.json"
    )

    with open(summary_file, "w", encoding="utf-8") as file:

        json.dump(
            summary,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nGenerated files:")

    print(validated_file)

    print(flagged_file)

    print(summary_file)


# ------------------------------------------------------------
# STEP 17: RUN COMPLETE VALIDATION PIPELINE
# ------------------------------------------------------------

def run_validation_pipeline():

    print("\n======================================")

    print("FINANCEMATE AI VALIDATION STARTED")

    print("======================================")

    total_valid = 0
    total_flagged = 0

    # Process all three cleaned datasets
    for dataset_name, config in DATASET_CONFIG.items():

        input_file = (
            PROCESSED_FOLDER / config["file"]
        )

        # Check input file
        if not input_file.is_file():

            raise FileNotFoundError(
                f"Cleaned dataset not found: {input_file}. "
                "Run the cleaning pipeline first."
            )

        # Read cleaned CSV
        df = pd.read_csv(input_file)

        # Validate records
        validated_df, summary = validate_dataframe(
            df,
            dataset_name
        )

        # Save results
        save_validation_results(
            validated_df,
            summary,
            dataset_name
        )

        total_valid += summary["valid_records"]

        total_flagged += summary["flagged_records"]

    # Final summary
    print("\n======================================")

    print("VALIDATION PIPELINE COMPLETED")

    print("======================================")

    print("Total valid records:", total_valid)

    print("Total flagged records:", total_flagged)


# ------------------------------------------------------------
# STEP 18: PROGRAM ENTRY POINT
# ------------------------------------------------------------

if __name__ == "__main__":

    run_validation_pipeline()
