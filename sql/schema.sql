
-- =========================================================
-- FINANCEMATE AI
-- POSTGRESQL DATABASE SCHEMA
-- =========================================================


-- STEP 1: PIPELINE EXECUTION HISTORY

CREATE TABLE IF NOT EXISTS pipeline_runs (

    run_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    pipeline_name VARCHAR(100) NOT NULL,

    status VARCHAR(30) NOT NULL,

    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    completed_at TIMESTAMP,

    total_records INTEGER DEFAULT 0,

    error_message TEXT

);


-- STEP 2: SALES TRANSACTIONS

CREATE TABLE IF NOT EXISTS sales_transactions (

    transaction_id VARCHAR(100) PRIMARY KEY,

    transaction_date DATE NOT NULL,

    description TEXT,

    category VARCHAR(100),

    department VARCHAR(100),

    amount NUMERIC(15,2) NOT NULL CHECK (amount > 0),

    payment_mode VARCHAR(100),

    status VARCHAR(30) NOT NULL,

    reference_id VARCHAR(100),

    source_row_number INTEGER,

    source_file VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- STEP 3: EXPENSE TRANSACTIONS

CREATE TABLE IF NOT EXISTS expense_transactions (

    transaction_id VARCHAR(100) PRIMARY KEY,

    transaction_date DATE NOT NULL,

    description TEXT,

    category VARCHAR(100),

    department VARCHAR(100),

    amount NUMERIC(15,2) NOT NULL CHECK (amount > 0),

    payment_mode VARCHAR(100),

    status VARCHAR(30) NOT NULL,

    reference_id VARCHAR(100),

    source_row_number INTEGER,

    source_file VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- STEP 4: BANK TRANSACTIONS

CREATE TABLE IF NOT EXISTS bank_transactions (

    bank_transaction_id VARCHAR(100) PRIMARY KEY,

    transaction_date DATE NOT NULL,

    description TEXT,

    amount NUMERIC(15,2) NOT NULL CHECK (amount > 0),

    transaction_type VARCHAR(30) NOT NULL
        CHECK (transaction_type IN ('Credit', 'Debit')),

    reference_id VARCHAR(100),

    source_row_number INTEGER,

    source_file VARCHAR(255),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- STEP 5: RECONCILIATION RESULTS

CREATE TABLE IF NOT EXISTS reconciliation_results (

    reconciliation_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    run_id BIGINT REFERENCES pipeline_runs(run_id),

    reference_id VARCHAR(100),

    company_transaction_id VARCHAR(100),

    bank_transaction_id VARCHAR(100),

    company_amount NUMERIC(15,2),

    bank_amount NUMERIC(15,2),

    amount_difference NUMERIC(15,2),

    reconciliation_status VARCHAR(60) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);


-- STEP 6: CREATE INDEXES FOR FASTER SEARCHING

CREATE INDEX IF NOT EXISTS idx_sales_reference
ON sales_transactions(reference_id);

CREATE INDEX IF NOT EXISTS idx_expense_reference
ON expense_transactions(reference_id);

CREATE INDEX IF NOT EXISTS idx_bank_reference
ON bank_transactions(reference_id);

CREATE INDEX IF NOT EXISTS idx_sales_date
ON sales_transactions(transaction_date);

CREATE INDEX IF NOT EXISTS idx_expense_date
ON expense_transactions(transaction_date);

CREATE INDEX IF NOT EXISTS idx_bank_date
ON bank_transactions(transaction_date);

CREATE INDEX IF NOT EXISTS idx_reconciliation_status
ON reconciliation_results(reconciliation_status);


-- =========================================================
-- DATABASE SCHEMA CREATION COMPLETED
-- =========================================================
