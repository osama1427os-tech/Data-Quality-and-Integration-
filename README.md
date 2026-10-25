# Data Quality and Integration

## Project Overview
This project demonstrates a practical data-quality workflow on a small transaction dataset containing records from CRM and ERP source systems. It identifies missing values, exact duplicate rows, repeated transaction IDs, and records that require manual review before integration.

> **Privacy note:** The public sample uses anonymized customer labels. Do not commit the original workbook or real customer-identifying data to a public repository.

## Objectives
- Inspect data completeness and consistency.
- Identify exact duplicate rows separately from possible transaction-ID conflicts.
- Generate a row-level issue log for review.
- Export a conservative exact-deduplicated dataset.
- Summarize source-system coverage and create basic quality charts.

## Dataset
The sample contains transaction ID, customer label, product, amount, date, status, and source system. The data is illustrative and small; findings should not be generalized beyond this dataset.

## Data Quality Rules
1. Trim surrounding whitespace and standardize transaction IDs to uppercase.
2. Parse amount and date fields into appropriate types.
3. Flag missing required values rather than inventing replacements.
4. Mark exact duplicate rows separately.
5. Flag repeated transaction IDs for investigation. A repeated ID is **not automatically treated as a duplicate**, because dates, source systems, or transaction states may differ.
6. Remove only exact duplicate rows in the conservative output.

## Repository Structure
```text
data-quality-integration/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   │   └── transactions_sample.csv
│   └── processed/
│       ├── data_quality_issues.csv
│       ├── summary_metrics.csv
│       ├── transactions_exact_deduplicated.csv
│       └── transactions_with_quality_flags.csv
├── reports/
│   └── figures/
│       ├── missing_values_by_column.png
│       └── source_system_counts.png
└── src/
    └── analyze_data.py
```

## How to Run
1. Install Python 3.10 or later.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the analysis from the repository root:
   ```bash
   python src/analyze_data.py
   ```

## Outputs
- `summary_metrics.csv`: high-level data-quality metrics.
- `data_quality_issues.csv`: row-level issues and recommended review actions.
- `transactions_with_quality_flags.csv`: dataset with duplicate and ID-review flags.
- `transactions_exact_deduplicated.csv`: output with exact duplicate rows removed.
- `reports/figures/`: generated charts.

## Optional SQL Extension\n`sql/quality_checks.sql` contains example staging-table and quality-check queries for a future SQL-based integration stage. These queries are illustrative and have not been run against a database in this project.\n\n## Limitations and Next Steps
- Repeated IDs and spelling variants require business rules or source-system confirmation before records are merged.
- The dataset is small and illustrative.
- A next iteration could add automated tests, configurable validation rules, SQL staging tables, and a documented integration strategy.
