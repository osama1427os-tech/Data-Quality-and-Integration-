-- Optional SQL extension for a future integration stage.
-- This schema is illustrative; the current analysis is run in Python on the anonymized CSV.
CREATE TABLE transactions_staging (
    transaction_id VARCHAR(30),
    customer_name VARCHAR(80),
    product VARCHAR(80),
    amount DECIMAL(12, 2),
    transaction_date DATE,
    status VARCHAR(30),
    source_system VARCHAR(20)
);

-- Quality check: missing required values
SELECT *
FROM transactions_staging
WHERE transaction_id IS NULL
   OR product IS NULL
   OR amount IS NULL
   OR transaction_date IS NULL
   OR source_system IS NULL;

-- Quality check: repeated transaction IDs for review (not automatic deletion)
SELECT transaction_id, COUNT(*) AS record_count
FROM transactions_staging
GROUP BY transaction_id
HAVING COUNT(*) > 1;

-- Exact duplicate detection should compare all relevant business columns.
SELECT transaction_id, customer_name, product, amount,
       transaction_date, status, source_system, COUNT(*) AS record_count
FROM transactions_staging
GROUP BY transaction_id, customer_name, product, amount,
         transaction_date, status, source_system
HAVING COUNT(*) > 1;
