
# ==========================================
# FINANCEMATE AI
# Financial Data Ingestion System
# ==========================================

# STEP 1: Import required libraries

import pandas as pd
from pathlib import Path


# STEP 2: Find the project folder

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# STEP 3: Find the raw data folder

RAW_DATA_FOLDER = PROJECT_ROOT / "data" / "raw"


# STEP 4: Function to read an Excel file

def read_excel_file(file_path):

    # Convert the file location into a Path object
    file_path = Path(file_path)

    # Check whether the file exists
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check the file extension
    if file_path.suffix.lower() not in [".xlsx", ".xlsm"]:
        raise ValueError("Please upload a valid Excel file.")

    # Read Excel data using Pandas
    df = pd.read_excel(file_path, engine="openpyxl")

    # Check whether the file contains data
    if df.empty:
        raise ValueError("The Excel file is empty.")

    # Return the loaded data
    return df


# STEP 5: Function to load all financial files

def load_financial_files():

    print("\nLoading financial files...")

    # Read sales Excel file
    sales_df = read_excel_file(
        RAW_DATA_FOLDER / "sales.xlsx"
    )

    # Read expenses Excel file
    expenses_df = read_excel_file(
        RAW_DATA_FOLDER / "expenses.xlsx"
    )

    # Read bank statement Excel file
    bank_df = read_excel_file(
        RAW_DATA_FOLDER / "bank_statement.xlsx"
    )

    print("All files loaded successfully!")

    return sales_df, expenses_df, bank_df


# STEP 6: Function to inspect a dataset

def inspect_dataframe(df, dataset_name):

    print("\n" + "=" * 50)

    print(f"DATASET: {dataset_name}")

    print("=" * 50)

    # Display first five records
    print("\nFirst five records:")
    print(df.head())

    # Display last five records
    print("\nLast five records:")
    print(df.tail())

    # Display total rows and columns
    print("\nDataset dimensions:")
    print(df.shape)

    # Display column names
    print("\nColumn names:")
    print(df.columns.tolist())

    # Display data types
    print("\nData types:")
    print(df.dtypes)

    # Display dataset information
    print("\nDataset information:")
    df.info()

    # Display statistical summary
    print("\nStatistical summary:")
    print(df.describe(include="all"))

    # Count missing values
    print("\nMissing values:")
    print(df.isnull().sum())

    # Count completely duplicated rows
    print("\nDuplicate rows:")
    print(df.duplicated().sum())

    # Calculate memory usage
    memory_mb = (
        df.memory_usage(deep=True).sum() / (1024 ** 2)
    )

    print(f"\nMemory usage: {memory_mb:.2f} MB")


# STEP 7: Main program

if __name__ == "__main__":

    # Load all three financial datasets
    sales_df, expenses_df, bank_df = load_financial_files()

    # Inspect sales data
    inspect_dataframe(sales_df, "SALES DATA")

    # Inspect expense data
    inspect_dataframe(expenses_df, "EXPENSE DATA")

    # Inspect bank statement
    inspect_dataframe(bank_df, "BANK STATEMENT")

    print("\n===================================")
    print("FINANCEMATE AI INGESTION COMPLETED")
    print("===================================")
