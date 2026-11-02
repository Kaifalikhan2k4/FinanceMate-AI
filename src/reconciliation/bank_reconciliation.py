
# ============================================================
# FINANCEMATE AI
# BANK RECONCILIATION ENGINE
# ============================================================

import pandas as pd
import json

from pathlib import Path


# ------------------------------------------------------------
# STEP 1: PROJECT PATHS
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_FOLDER = PROJECT_ROOT / "data" / "processed"
REPORTS_FOLDER = PROJECT_ROOT / "data" / "reports"

PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)
REPORTS_FOLDER.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# STEP 2: LOAD VALIDATED FINANCIAL DATA
# ------------------------------------------------------------

def load_reconciliation_data():

    sales = pd.read_csv(
        PROCESSED_FOLDER / "sales_validated.csv"
    )

    expenses = pd.read_csv(
        PROCESSED_FOLDER / "expenses_validated.csv"
    )

    bank = pd.read_csv(
        PROCESSED_FOLDER / "bank_statement_validated.csv"
    )

    return sales, expenses, bank


# ------------------------------------------------------------
# STEP 3: PREPARE COMPANY TRANSACTIONS
# ------------------------------------------------------------

def prepare_company_transactions(sales, expenses):

    # Only completed company transactions should be
    # expected to appear in the bank statement.

    sales = sales[
        sales["status"].str.strip().str.lower() == "completed"
    ].copy()

    expenses = expenses[
        expenses["status"].str.strip().str.lower() == "completed"
    ].copy()

    # Sales should appear as bank credits
    sales["expected_bank_type"] = "Credit"

    # Expenses should appear as bank debits
    expenses["expected_bank_type"] = "Debit"

    # Combine sales and expenses
    company = pd.concat(
        [sales, expenses],
        ignore_index=True
    )

    # Keep important reconciliation columns
    company = company[
        [
            "transaction_id",
            "date",
            "description",
            "amount",
            "reference_id",
            "expected_bank_type"
        ]
    ].copy()

    company = company.rename(
        columns={
            "transaction_id": "company_transaction_id",
            "date": "company_date",
            "description": "company_description",
            "amount": "company_amount"
        }
    )

    return company


# ------------------------------------------------------------
# STEP 4: PREPARE BANK TRANSACTIONS
# ------------------------------------------------------------

def prepare_bank_transactions(bank):

    bank = bank.copy()

    bank = bank[
        [
            "bank_transaction_id",
            "date",
            "description",
            "amount",
            "transaction_type",
            "reference_id"
        ]
    ]

    bank = bank.rename(
        columns={
            "date": "bank_date",
            "description": "bank_description",
            "amount": "bank_amount",
            "transaction_type": "bank_transaction_type"
        }
    )

    return bank


# ------------------------------------------------------------
# STEP 5: RECONCILE TRANSACTIONS
# ------------------------------------------------------------

def reconcile_transactions(company, bank):

    print("\nStarting bank reconciliation...")

    # Check whether reference IDs are available
    # A missing reference cannot be safely matched.

    company_missing_ref = company[
        company["reference_id"].isna()
        | company["reference_id"].astype(str).str.strip().eq("")
    ].copy()

    bank_missing_ref = bank[
        bank["reference_id"].isna()
        | bank["reference_id"].astype(str).str.strip().eq("")
    ].copy()

    # Only records with references can enter matching
    company_matchable = company.drop(
        company_missing_ref.index
    )

    bank_matchable = bank.drop(
        bank_missing_ref.index
    )

    # Detect duplicate reference IDs.
    # We will not make arbitrary many-to-many matches.

    company_duplicate_refs = company_matchable[
        company_matchable.duplicated(
            subset=["reference_id"],
            keep=False
        )
    ].copy()

    bank_duplicate_refs = bank_matchable[
        bank_matchable.duplicated(
            subset=["reference_id"],
            keep=False
        )
    ].copy()

    # Exclude ambiguous reference IDs from automatic matching
    company_ambiguous_refs = set(
        company_duplicate_refs["reference_id"]
    )

    bank_ambiguous_refs = set(
        bank_duplicate_refs["reference_id"]
    )

    ambiguous_refs = (
        company_ambiguous_refs | bank_ambiguous_refs
    )

    company_unique = company_matchable[
        ~company_matchable["reference_id"].isin(
            ambiguous_refs
        )
    ]

    bank_unique = bank_matchable[
        ~bank_matchable["reference_id"].isin(
            ambiguous_refs
        )
    ]

    # --------------------------------------------------------
    # MATCH USING REFERENCE ID
    # --------------------------------------------------------

    result = pd.merge(
        company_unique,
        bank_unique,
        on="reference_id",
        how="outer",
        indicator=True
    )

    # --------------------------------------------------------
    # CLASSIFY RECONCILIATION RESULTS
    # --------------------------------------------------------

    conditions = [

        result["_merge"] == "left_only",

        result["_merge"] == "right_only",

        (
            (result["_merge"] == "both")
            &
            (
                result["company_amount"]
                != result["bank_amount"]
            )
        ),

        (
            (result["_merge"] == "both")
            &
            (
                result["expected_bank_type"]
                != result["bank_transaction_type"]
            )
        )

    ]

    statuses = [

        "UNMATCHED_COMPANY_TRANSACTION",

        "UNMATCHED_BANK_TRANSACTION",

        "AMOUNT_DISCREPANCY",

        "TRANSACTION_TYPE_MISMATCH"

    ]

    result["reconciliation_status"] = "MATCHED"

    for condition, status in zip(conditions, statuses):

        result.loc[
            condition,
            "reconciliation_status"
        ] = status

    # --------------------------------------------------------
    # CALCULATE AMOUNT DIFFERENCE
    # --------------------------------------------------------

    result["amount_difference"] = (
        result["bank_amount"]
        - result["company_amount"]
    )

    # --------------------------------------------------------
    # ADD AMBIGUOUS AND MISSING REFERENCE RECORDS
    # --------------------------------------------------------

    company_ambiguous = company_duplicate_refs.copy()

    company_ambiguous["reconciliation_status"] = (
        "AMBIGUOUS_COMPANY_REFERENCE"
    )

    bank_ambiguous = bank_duplicate_refs.copy()

    bank_ambiguous["reconciliation_status"] = (
        "AMBIGUOUS_BANK_REFERENCE"
    )

    company_missing_ref["reconciliation_status"] = (
        "MISSING_COMPANY_REFERENCE"
    )

    bank_missing_ref["reconciliation_status"] = (
        "MISSING_BANK_REFERENCE"
    )

    # Align the different record structures
    all_columns = result.columns.tolist()

    for frame in [
        company_ambiguous,
        bank_ambiguous,
        company_missing_ref,
        bank_missing_ref
    ]:

        for column in all_columns:

            if column not in frame.columns:
                frame[column] = pd.NA

    # Combine all reconciliation results
    final_result = pd.concat(
        [
            result,
            company_ambiguous[all_columns],
            bank_ambiguous[all_columns],
            company_missing_ref[all_columns],
            bank_missing_ref[all_columns]
        ],
        ignore_index=True
    )

    # Remove the internal merge indicator
    final_result = final_result.drop(
        columns=["_merge"]
    )

    print("Reconciliation completed!")

    return final_result


# ------------------------------------------------------------
# STEP 6: GENERATE RECONCILIATION SUMMARY
# ------------------------------------------------------------

def generate_summary(result):

    status_counts = (
        result["reconciliation_status"]
        .value_counts()
        .to_dict()
    )

    summary = {

        "total_reconciliation_results": len(result),

        "matched": status_counts.get("MATCHED", 0),

        "amount_discrepancies": status_counts.get(
            "AMOUNT_DISCREPANCY", 0
        ),

        "unmatched_bank_transactions": status_counts.get(
            "UNMATCHED_BANK_TRANSACTION", 0
        ),

        "unmatched_company_transactions": status_counts.get(
            "UNMATCHED_COMPANY_TRANSACTION", 0
        ),

        "other_issues": sum(
            count for status, count in status_counts.items()
            if status not in [
                "MATCHED",
                "AMOUNT_DISCREPANCY",
                "UNMATCHED_BANK_TRANSACTION",
                "UNMATCHED_COMPANY_TRANSACTION"
            ]
        ),

        "status_counts": status_counts

    }

    return summary


# ------------------------------------------------------------
# STEP 7: SAVE RECONCILIATION REPORTS
# ------------------------------------------------------------

def save_reconciliation_results(result, summary):

    # Save complete reconciliation results
    result.to_csv(
        REPORTS_FOLDER / "reconciliation_results.csv",
        index=False
    )

    # Save only transactions requiring investigation
    issues = result[
        result["reconciliation_status"] != "MATCHED"
    ].copy()

    issues.to_csv(
        REPORTS_FOLDER / "reconciliation_issues.csv",
        index=False
    )

    # Save JSON summary
    with open(
        REPORTS_FOLDER / "reconciliation_summary.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nReports saved successfully!")


# ------------------------------------------------------------
# STEP 8: MAIN RECONCILIATION PIPELINE
# ------------------------------------------------------------

def run_reconciliation_pipeline():

    print("\n======================================")

    print("FINANCEMATE AI BANK RECONCILIATION")

    print("======================================")

    # Load datasets
    sales, expenses, bank = load_reconciliation_data()

    # Prepare company records
    company = prepare_company_transactions(
        sales,
        expenses
    )

    # Prepare bank records
    bank = prepare_bank_transactions(bank)

    # Run reconciliation
    result = reconcile_transactions(
        company,
        bank
    )

    # Generate summary
    summary = generate_summary(result)

    # Save reports
    save_reconciliation_results(
        result,
        summary
    )

    # Display results
    print("\n========== RECONCILIATION SUMMARY ==========")

    for key, value in summary.items():

        print(f"{key}: {value}")

    print("\n========== RECONCILIATION DETAILS ==========")

    print(
        result[
            [
                "reference_id",
                "company_amount",
                "bank_amount",
                "amount_difference",
                "reconciliation_status"
            ]
        ].to_string(index=False)
    )

    print("\nBANK RECONCILIATION COMPLETED!")


# ------------------------------------------------------------
# STEP 9: EXECUTE PROGRAM
# ------------------------------------------------------------

if __name__ == "__main__":

    run_reconciliation_pipeline()
