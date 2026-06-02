import sys
import io
import pandas as pd
from pathlib import Path

# Fix Unicode output on Windows terminals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "clean"

RAW_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

excel_files = {
    "companies": "companies.xlsx",
    "balancesheet": "balancesheet.xlsx",
    "profitandloss": "profitandloss.xlsx",
    "cashflow": "cashflow.xlsx",
    "analysis": "analysis.xlsx",
    "prosandcons": "prosandcons.xlsx",
    "documents": "documents.xlsx"
}

print("[*] Starting Data Extraction...\n")

for table_name, filename in excel_files.items():
    filepath = RAW_DIR / filename
    if filepath.exists():
        try:
            # header=1 skips the title row (row 0) and uses row 1 as column names
            df = pd.read_excel(filepath, header=1)
            output_path = CLEAN_DIR / f"{table_name}.csv"
            df.to_csv(output_path, index=False)
            print(f"[OK] {table_name}: {len(df)} rows -> saved to clean/")
        except Exception as e:
            print(f"[ERROR] {filename}: {e}")
    else:
        print(f"[WARN] File not found: {filename}")

print("\n[DONE] Extraction completed! Check 'data/clean/' folder.")
