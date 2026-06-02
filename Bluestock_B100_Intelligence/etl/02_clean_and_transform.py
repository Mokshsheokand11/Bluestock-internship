import sys
import io
import pandas as pd
from pathlib import Path
import numpy as np

# Fix Unicode output on Windows terminals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_DIR = BASE_DIR / "data" / "clean"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

print("[*] Starting Data Cleaning & Transformation...\n")

# ─────────────────────────────────────────────
# 1. Load & clean Companies
# ─────────────────────────────────────────────
companies = pd.read_csv(CLEAN_DIR / "companies.csv")
print(f"Companies loaded: {len(companies)} rows")
print(f"  Columns: {list(companies.columns)}\n")

# Strip whitespace from string columns if they exist
if 'company_name' in companies.columns:
    companies['company_name'] = companies['company_name'].str.strip()
if 'symbol' in companies.columns:
    companies['symbol'] = companies['symbol'].str.strip().str.upper()

# Sector mapping
sector_map = {
    'TCS': 'IT', 'INFY': 'IT', 'WIPRO': 'IT', 'HCLTECH': 'IT',
    'HDFCBANK': 'Banking', 'ICICIBANK': 'Banking', 'AXISBANK': 'Banking',
    'RELIANCE': 'Energy', 'ADANIENT': 'Energy', 'ADANIPOWER': 'Energy',
    'SBILIFE': 'Insurance', 'HDFCLIFE': 'Insurance',
    'BAJFINANCE': 'NBFC', 'BAJAJFINSV': 'NBFC',
    'ASIANPAINT': 'Consumer', 'HINDUNILVR': 'Consumer',
    'SUNPHARMA': 'Pharma', 'DRREDDY': 'Pharma',
    'MARUTI': 'Auto', 'TATAMOTORS': 'Auto',
}

if 'symbol' in companies.columns:
    companies['sector'] = companies['symbol'].map(sector_map).fillna('Other')

companies.to_csv(PROCESSED_DIR / "companies_clean.csv", index=False)
print("[OK] Companies cleaned and sector added")

# ─────────────────────────────────────────────
# 2. Load & clean Profit & Loss
# ─────────────────────────────────────────────
try:
    pnl = pd.read_csv(CLEAN_DIR / "profitandloss.csv")
    print(f"\nProfit & Loss loaded: {len(pnl)} rows")
    print(f"  Columns: {list(pnl.columns)}")

    # Calculate net profit margin if the right columns exist
    if 'net_profit' in pnl.columns and 'sales' in pnl.columns:
        pnl['net_profit_margin'] = (pnl['net_profit'] / pnl['sales'] * 100).round(2)
        print("  -> net_profit_margin calculated")

    pnl.to_csv(PROCESSED_DIR / "profitandloss_clean.csv", index=False)
    print("[OK] Profit & Loss cleaned")
except FileNotFoundError:
    print("[WARN] profitandloss.csv not found — skipping")
except Exception as e:
    print(f"[ERROR] Could not process profitandloss: {e}")

# ─────────────────────────────────────────────
# 3. Load & clean Balance Sheet
# ─────────────────────────────────────────────
try:
    bs = pd.read_csv(CLEAN_DIR / "balancesheet.csv")
    print(f"\nBalance Sheet loaded: {len(bs)} rows")
    print(f"  Columns: {list(bs.columns)}")

    # Debt-to-Equity ratio if columns exist
    if 'total_debt' in bs.columns and 'total_equity' in bs.columns:
        bs['debt_to_equity'] = (bs['total_debt'] / bs['total_equity'].replace(0, np.nan)).round(2)
        print("  -> debt_to_equity calculated")

    bs.to_csv(PROCESSED_DIR / "balancesheet_clean.csv", index=False)
    print("[OK] Balance Sheet cleaned")
except FileNotFoundError:
    print("[WARN] balancesheet.csv not found — skipping")
except Exception as e:
    print(f"[ERROR] Could not process balancesheet: {e}")

# ─────────────────────────────────────────────
# 4. Load & clean Cash Flow
# ─────────────────────────────────────────────
try:
    cf = pd.read_csv(CLEAN_DIR / "cashflow.csv")
    print(f"\nCash Flow loaded: {len(cf)} rows")
    print(f"  Columns: {list(cf.columns)}")

    cf.to_csv(PROCESSED_DIR / "cashflow_clean.csv", index=False)
    print("[OK] Cash Flow cleaned")
except FileNotFoundError:
    print("[WARN] cashflow.csv not found — skipping")
except Exception as e:
    print(f"[ERROR] Could not process cashflow: {e}")

# ─────────────────────────────────────────────
# 5. Load & clean Analysis
# ─────────────────────────────────────────────
try:
    analysis = pd.read_csv(CLEAN_DIR / "analysis.csv")
    print(f"\nAnalysis loaded: {len(analysis)} rows")
    print(f"  Columns: {list(analysis.columns)}")

    analysis.to_csv(PROCESSED_DIR / "analysis_clean.csv", index=False)
    print("[OK] Analysis cleaned")
except FileNotFoundError:
    print("[WARN] analysis.csv not found — skipping")
except Exception as e:
    print(f"[ERROR] Could not process analysis: {e}")

# ─────────────────────────────────────────────
# 6. Load & clean Documents
# ─────────────────────────────────────────────
try:
    docs = pd.read_csv(CLEAN_DIR / "documents.csv")
    print(f"\nDocuments loaded: {len(docs)} rows")
    print(f"  Columns: {list(docs.columns)}")

    docs.to_csv(PROCESSED_DIR / "documents_clean.csv", index=False)
    print("[OK] Documents cleaned")
except FileNotFoundError:
    print("[WARN] documents.csv not found — skipping")
except Exception as e:
    print(f"[ERROR] Could not process documents: {e}")

# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────
print("\n[DONE] Cleaning & Transformation completed!")
print(f"Processed files saved in: {PROCESSED_DIR}")

processed_files = list(PROCESSED_DIR.glob("*.csv"))
print(f"\nFiles in data/processed/ ({len(processed_files)} total):")
for f in processed_files:
    print(f"  -> {f.name}")
