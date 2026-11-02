
import pandas as pd
from pathlib import Path

# 1. Define the location where Excel files will be saved
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_FOLDER = PROJECT_ROOT / "data" / "raw"

# Create the folder if it does not exist
RAW_DATA_FOLDER.mkdir(parents=True, exist_ok=True)


# 2. Create sample sales data
sales_data = [
    {
        "transaction_id": "SAL001",
        "date": "2026-10-01",
        "description": "Website Development",
        "category": "Sales",
        "department": "IT",
        "amount": 50000,
        "payment_mode": "Bank Transfer",
        "status": "Completed",
        "reference_id": "REF001"
    },
    {
        "transaction_id": "SAL002",
        "date": "2026-10-02",
        "description": "Software Subscription",
        "category": "Sales",
        "department": "IT",
        "amount": 25000,
        "payment_mode": "UPI",
        "status": "Completed",
        "reference_id": "REF002"
    },
    {
        "transaction_id": "SAL003",
        "date": "2026-10-03",
        "description": "Consulting Services",
        "category": "Sales",
        "department": "Finance",
        "amount": 40000,
        "payment_mode": "Bank Transfer",
        "status": "Completed",
        "reference_id": "REF003"
    },
    {
        "transaction_id": "SAL004",
        "date": "2026-10-04",
        "description": "Cloud Services",
        "category": "Sales",
        "department": "IT",
        "amount": 30000,
        "payment_mode": "UPI",
        "status": "Pending",
        "reference_id": "REF004"
    },
    {
        "transaction_id": "SAL005",
        "date": "2026-10-05",
        "description": "Digital Marketing",
        "category": "Sales",
        "department": "Marketing",
        "amount": 20000,
        "payment_mode": "Bank Transfer",
        "status": "Completed",
        "reference_id": "REF005"
    }
]

# 3. Create sample expenses data
expenses_data = [
    {
        "transaction_id": "EXP001",
        "date": "2026-10-01",
        "description": "Office Rent",
        "category": "Expense",
        "department": "Administration",
        "amount": 30000,
        "payment_mode": "Bank Transfer",
        "status": "Completed",
        "reference_id": "REF101"
    },
    {
        "transaction_id": "EXP002",
        "date": "2026-10-02",
        "description": "Employee Salaries",
        "category": "Expense",
        "department": "HR",
        "amount": 45000,
        "payment_mode": "Bank Transfer",
        "status": "Completed",
        "reference_id": "REF102"
    },
    {
        "transaction_id": "EXP003",
        "date": "2026-10-03",
        "description": "Office Supplies",
        "category": "Expense",
        "department": "Administration",
        "amount": 15000,
        "payment_mode": "UPI",
        "status": "Completed",
        "reference_id": "REF103"
    },
    {
        "transaction_id": "EXP003",
        "date": "2026-10-03",
        "description": "Office Supplies",
        "category": "Expense",
        "department": "Administration",
        "amount": 15000,
        "payment_mode": "UPI",
        "status": "Completed",
        "reference_id": "REF103"
    },
    {
        "transaction_id": "EXP005",
        "date": "not-a-date",
        "description": "Internet Bill",
        "category": "Expense",
        "department": None,
        "amount": -5000,
        "payment_mode": "Cash",
        "status": "Completed",
        "reference_id": "REF105"
    }
]

# 4. Create sample bank statement data
bank_data = [
    {
        "bank_transaction_id": "BNK001",
        "date": "2026-10-01",
        "description": "Website Development Payment",
        "amount": 50000,
        "transaction_type": "Credit",
        "reference_id": "REF001"
    },
    {
        "bank_transaction_id": "BNK002",
        "date": "2026-10-02",
        "description": "Software Subscription Payment",
        "amount": 25000,
        "transaction_type": "Credit",
        "reference_id": "REF002"
    },
    {
        "bank_transaction_id": "BNK003",
        "date": "2026-10-01",
        "description": "Office Rent Payment",
        "amount": 30000,
        "transaction_type": "Debit",
        "reference_id": "REF101"
    },
    {
        "bank_transaction_id": "BNK004",
        "date": "2026-10-02",
        "description": "Salary Payment",
        "amount": 45000,
        "transaction_type": "Debit",
        "reference_id": "REF102"
    },
    {
        "bank_transaction_id": "BNK005",
        "date": "2026-10-03",
        "description": "Office Supplies Payment",
        "amount": 18000,
        "transaction_type": "Debit",
        "reference_id": "REF103"
    },
    {
        "bank_transaction_id": "BNK006",
        "date": "2026-10-06",
        "description": "Unknown Bank Credit",
        "amount": 12000,
        "transaction_type": "Credit",
        "reference_id": "REF999"
    }
]

# 5. Convert Python data into Pandas DataFrames
sales_df = pd.DataFrame(sales_data)
expenses_df = pd.DataFrame(expenses_data)
bank_df = pd.DataFrame(bank_data)

# 6. Save DataFrames as Excel files
sales_df.to_excel(RAW_DATA_FOLDER / "sales.xlsx", index=False)

expenses_df.to_excel(RAW_DATA_FOLDER / "expenses.xlsx", index=False)

bank_df.to_excel(RAW_DATA_FOLDER / "bank_statement.xlsx", index=False)

# 7. Display confirmation
print("FinanceMate AI datasets created successfully!")

print("Sales records:", len(sales_df))
print("Expense records:", len(expenses_df))
print("Bank records:", len(bank_df))

print("Files saved in:", RAW_DATA_FOLDER)
