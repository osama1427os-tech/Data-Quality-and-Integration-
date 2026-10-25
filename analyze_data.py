"""
Data Quality and Integration
Run from the repository root:
    python src/analyze_data.py

Uses the anonymized sample dataset so the repository can be public safely.
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "raw" / "transactions_sample.csv"
OUT = ROOT / "data" / "processed"
FIG = ROOT / "reports" / "figures"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(INPUT)
expected = [
    "Transaction ID", "Customer Name", "Product", "Amount",
    "Date", "Status", "Source System"
]
missing_columns = sorted(set(expected) - set(df.columns))
if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

# Preserve a copy for auditability and normalize text fields conservatively.
df["Transaction ID"] = df["Transaction ID"].astype("string").str.strip().str.upper()
for col in ["Customer Name", "Product", "Status", "Source System"]:
    df[col] = df[col].astype("string").str.strip()

df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Exact duplicates: all columns match after basic whitespace/type normalization.
exact_duplicate_mask = df.duplicated(keep="first")
df["Exact Duplicate"] = exact_duplicate_mask

# Potential transaction-ID conflicts are flagged for review, not automatically removed.
df["Transaction ID Count"] = df.groupby("Transaction ID")["Transaction ID"].transform("size")
df["Needs ID Review"] = df["Transaction ID Count"] > 1

# Build a row-level issue log.
issues = []
for idx, row in df.iterrows():
    row_num = idx + 2  # CSV header is row 1
    for col in expected:
        if pd.isna(row[col]) or (isinstance(row[col], str) and not row[col].strip()):
            issues.append({
                "source_row": row_num,
                "transaction_id": row.get("Transaction ID", ""),
                "issue_type": "Missing value",
                "field": col,
                "details": f"{col} is blank; do not impute without a business rule."
            })
    if row["Needs ID Review"]:
        issues.append({
            "source_row": row_num,
            "transaction_id": row["Transaction ID"],
            "issue_type": "Repeated transaction ID",
            "field": "Transaction ID",
            "details": "Review against date, amount, product, status and source system before merging or deleting."
        })
    if row["Exact Duplicate"]:
        issues.append({
            "source_row": row_num,
            "transaction_id": row["Transaction ID"],
            "issue_type": "Exact duplicate row",
            "field": "All fields",
            "details": "All normalized fields match an earlier row; candidate for removal after validation."
        })

issue_df = pd.DataFrame(issues)
issue_df.to_csv(OUT / "data_quality_issues.csv", index=False)

# Deduplicate only exact rows. Potential matches remain and are documented.
clean = df.loc[~exact_duplicate_mask].copy()
clean.drop(columns=["Exact Duplicate", "Transaction ID Count", "Needs ID Review"]).to_csv(
    OUT / "transactions_exact_deduplicated.csv", index=False
)
df.to_csv(OUT / "transactions_with_quality_flags.csv", index=False)

summary = {
    "source_rows": int(len(df)),
    "source_columns": int(len(expected)),
    "missing_cells_in_required_columns": int(df[expected].isna().sum().sum()),
    "rows_with_at_least_one_missing_value": int(df[expected].isna().any(axis=1).sum()),
    "exact_duplicate_rows_marked": int(exact_duplicate_mask.sum()),
    "rows_after_exact_deduplication": int(len(clean)),
    "rows_with_repeated_transaction_id": int(df["Needs ID Review"].sum()),
    "unique_source_systems": int(df["Source System"].nunique(dropna=True)),
}
pd.DataFrame([summary]).to_csv(OUT / "summary_metrics.csv", index=False)

# Plot source system distribution.
counts = df["Source System"].fillna("Missing").value_counts()
plt.figure(figsize=(6, 4))
counts.plot(kind="bar")
plt.title("Transactions by Source System")
plt.xlabel("Source System")
plt.ylabel("Number of Rows")
plt.tight_layout()
plt.savefig(FIG / "source_system_counts.png", dpi=160)
plt.close()

# Plot missing values per column.
missing = df[expected].isna().sum()
plt.figure(figsize=(8, 4))
missing.plot(kind="bar")
plt.title("Missing Values by Column")
plt.xlabel("Column")
plt.ylabel("Missing Cells")
plt.xticks(rotation=35, ha="right")
plt.tight_layout()
plt.savefig(FIG / "missing_values_by_column.png", dpi=160)
plt.close()

print("Analysis complete.")
print(pd.DataFrame([summary]).to_string(index=False))
print(f"Issue log: {OUT / 'data_quality_issues.csv'}")
