import sys
import io
import os
import django
import pandas as pd
import numpy as np
from pathlib import Path

# Fix Unicode output on Windows terminals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ─────────────────────────────────────────────
# Django Setup
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent      # Bluestock_B100_Intelligence/
BACKEND_DIR = BASE_DIR / "backend"                     # backend/
CLEAN_DIR = BASE_DIR / "data" / "clean"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bluestock.settings')
django.setup()

from api.models import Company, FinancialData

print("[*] Loading Profit & Loss + Balance Sheet data into Django...\n")

# ─────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────
def safe_int(val, default=0):
    if pd.isna(val):
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default

def safe_float(val, default=0.0):
    if pd.isna(val):
        return default
    try:
        return round(float(val), 4)
    except (ValueError, TypeError):
        return default

def extract_year(year_raw):
    """Extract 4-digit year from strings like 'Mar 2022', 'Dec 2021', '2023'."""
    digits = ''.join(filter(str.isdigit, str(year_raw)))
    if len(digits) >= 4:
        return int(digits[-4:])
    return None

# ─────────────────────────────────────────────
# STEP 1: Load Profit & Loss into FinancialData
# CSV columns: id, company_id, year, sales, expenses,
#              operating_profit, opm_percentage, other_income,
#              interest, depreciation, profit_before_tax,
#              tax_percentage, net_profit, eps, dividend_payout
# ─────────────────────────────────────────────
pnl_path = CLEAN_DIR / "profitandloss.csv"
if not pnl_path.exists():
    pnl_path = PROCESSED_DIR / "profitandloss_clean.csv"

pnl = pd.read_csv(pnl_path)
print(f"Profit & Loss rows: {len(pnl)}")
print(f"  Columns: {list(pnl.columns)[:8]} ...")

loaded_pnl = 0
skipped_pnl = 0

for _, row in pnl.iterrows():
    symbol = str(row.get('company_id', '')).strip().upper()
    year = extract_year(row.get('year', ''))

    if not symbol or not year:
        skipped_pnl += 1
        continue

    try:
        company = Company.objects.get(symbol=symbol)
    except Company.DoesNotExist:
        skipped_pnl += 1
        continue

    try:
        FinancialData.objects.update_or_create(
            company=company,
            year=year,
            defaults={
                'sales':      safe_int(row.get('sales', 0)),
                'net_profit': safe_int(row.get('net_profit', 0)),
                'opm_pct':    safe_float(row.get('opm_percentage', 0)),
                'eps':        safe_float(row.get('eps', 0)),
            }
        )
        loaded_pnl += 1
    except Exception as e:
        print(f"  [ERROR] P&L {symbol} {year}: {e}")
        skipped_pnl += 1

print(f"[OK] P&L loaded: {loaded_pnl} | Skipped: {skipped_pnl}\n")

# ─────────────────────────────────────────────
# STEP 2: Update FinancialData with Balance Sheet data
# CSV columns: id, company_id, year, equity_capital, reserves,
#              borrowings, other_liabilities, total_liabilities,
#              fixed_assets, cwip, investments, other_asset, total_assets
# ─────────────────────────────────────────────
bs_path = CLEAN_DIR / "balancesheet.csv"
if not bs_path.exists():
    bs_path = PROCESSED_DIR / "balancesheet_clean.csv"

bs = pd.read_csv(bs_path)
print(f"Balance Sheet rows: {len(bs)}")
print(f"  Columns: {list(bs.columns)[:8]} ...")

loaded_bs = 0
skipped_bs = 0

for _, row in bs.iterrows():
    symbol = str(row.get('company_id', '')).strip().upper()
    year = extract_year(row.get('year', ''))

    if not symbol or not year:
        skipped_bs += 1
        continue

    try:
        company = Company.objects.get(symbol=symbol)
    except Company.DoesNotExist:
        skipped_bs += 1
        continue

    borrowings    = safe_int(row.get('borrowings', 0))
    reserves      = safe_int(row.get('reserves', 0))
    total_assets  = safe_int(row.get('total_assets', 0))
    equity_cap    = safe_float(row.get('equity_capital', 0))
    total_equity  = equity_cap + reserves
    de_calc       = round(borrowings / total_equity, 2) if total_equity > 0 else 0.0

    try:
        # Update existing FinancialData row if it exists, otherwise create it
        FinancialData.objects.update_or_create(
            company=company,
            year=year,
            defaults={
                'total_assets':        total_assets,
                'borrowings':          borrowings,
                'reserves':            reserves,
                'debt_to_equity_calc': de_calc,
            }
        )
        loaded_bs += 1
    except Exception as e:
        print(f"  [ERROR] BS {symbol} {year}: {e}")
        skipped_bs += 1

print(f"[OK] Balance Sheet merged: {loaded_bs} | Skipped: {skipped_bs}\n")

# ─────────────────────────────────────────────
# STEP 3: Update Company-level aggregates
# ─────────────────────────────────────────────
updated_companies = 0
for company in Company.objects.all():
    fin_qs = FinancialData.objects.filter(company=company).order_by('-year')
    if not fin_qs.exists():
        continue

    latest = fin_qs.first()

    # Average OPM across all years (non-zero)
    opm_vals = [f.opm_pct for f in fin_qs if f.opm_pct != 0]
    avg_opm = round(sum(opm_vals) / len(opm_vals), 2) if opm_vals else company.opm

    # D/E from latest balance sheet year
    de = latest.debt_to_equity_calc if latest.debt_to_equity_calc else company.debt_to_equity

    # Revenue growth: (latest_sales - oldest_sales) / oldest_sales * 100
    all_fin = list(fin_qs.order_by('year'))
    rev_growth = company.revenue_growth
    if len(all_fin) >= 2:
        oldest_sales = all_fin[0].sales
        latest_sales = all_fin[-1].sales
        if oldest_sales > 0:
            n_years = all_fin[-1].year - all_fin[0].year
            if n_years > 0:
                cagr = ((latest_sales / oldest_sales) ** (1 / n_years) - 1) * 100
                rev_growth = round(cagr, 2)

    Company.objects.filter(symbol=company.symbol).update(
        opm=avg_opm,
        debt_to_equity=de,
        revenue_growth=rev_growth,
    )
    updated_companies += 1

print(f"[OK] Company aggregates updated for {updated_companies} companies\n")

# ─────────────────────────────────────────────
# STEP 4: Final Summary
# ─────────────────────────────────────────────
total_companies   = Company.objects.count()
total_financials  = FinancialData.objects.count()

print("=" * 55)
print("[DONE] Financial data loading complete!")
print(f"  Companies in DB    : {total_companies}")
print(f"  FinancialData rows : {total_financials}")
print("=" * 55)

print("\nTop 8 companies by health score:")
for c in Company.objects.order_by('-health_score')[:8]:
    print(f"  {c.symbol:<15} | Score:{c.health_score:>6} | ROE:{c.roe:>7}% | OPM:{c.opm:>7}% | D/E:{c.debt_to_equity:>5}")
