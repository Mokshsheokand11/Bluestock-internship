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
# manage.py lives in Bluestock_B100_Intelligence/
# Django apps live inside backend/, so we point
# sys.path at backend/ before calling django.setup()
# ─────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent          # Bluestock_B100_Intelligence/
BACKEND_DIR = BASE_DIR / "backend"                         # backend/
PROCESSED_DIR = BASE_DIR / "data" / "processed"

sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bluestock.settings')
django.setup()

from api.models import Company, FinancialData

print("[*] Loading cleaned data into Django database...\n")

# ─────────────────────────────────────────────
# Helper: safely get a numeric value from a row
# ─────────────────────────────────────────────
def safe_float(row, col, default=0.0):
    if col not in row.index:
        return default
    val = row[col]
    if pd.isna(val):
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def safe_int(row, col, default=0):
    if col not in row.index:
        return default
    val = row[col]
    if pd.isna(val):
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default

# ─────────────────────────────────────────────
# STEP 1: Load Companies
# id column = NSE symbol (primary key)
# ─────────────────────────────────────────────
companies_df = pd.read_csv(PROCESSED_DIR / "companies_clean.csv")
print(f"Companies to load: {len(companies_df)}")

sector_map = {
    'TCS': 'IT', 'INFY': 'IT', 'WIPRO': 'IT', 'HCLTECH': 'IT', 'TECHM': 'IT',
    'LTIM': 'IT', 'PERSISTENT': 'IT', 'MPHASIS': 'IT',
    'HDFCBANK': 'Banking', 'ICICIBANK': 'Banking', 'AXISBANK': 'Banking',
    'SBIN': 'Banking', 'KOTAKBANK': 'Banking', 'INDUSINDBK': 'Banking',
    'FEDERALBNK': 'Banking', 'BANDHANBNK': 'Banking',
    'RELIANCE': 'Energy', 'ADANIENT': 'Energy', 'ADANIPOWER': 'Energy',
    'ONGC': 'Energy', 'NTPC': 'Energy', 'POWERGRID': 'Energy', 'ADANIENSOL': 'Energy',
    'SBILIFE': 'Insurance', 'HDFCLIFE': 'Insurance', 'ICICIGI': 'Insurance',
    'BAJFINANCE': 'NBFC', 'BAJAJFINSV': 'NBFC', 'CHOLAFIN': 'NBFC',
    'ASIANPAINT': 'Consumer', 'HINDUNILVR': 'Consumer', 'NESTLEIND': 'Consumer',
    'BRITANNIA': 'Consumer', 'DABUR': 'Consumer', 'MARICO': 'Consumer',
    'SUNPHARMA': 'Pharma', 'DRREDDY': 'Pharma', 'CIPLA': 'Pharma',
    'DIVISLAB': 'Pharma', 'APOLLOHOSP': 'Healthcare',
    'MARUTI': 'Auto', 'TATAMOTORS': 'Auto', 'M&M': 'Auto', 'HEROMOTOCO': 'Auto',
    'EICHERMOT': 'Auto', 'BAJAJ-AUTO': 'Auto',
    'TATASTEEL': 'Metals', 'JSWSTEEL': 'Metals', 'HINDALCO': 'Metals',
    'ULTRACEMCO': 'Cement', 'GRASIM': 'Cement', 'SHREECEM': 'Cement',
    'BHARTIARTL': 'Telecom', 'IDEA': 'Telecom',
    'LT': 'Infrastructure', 'ADANIPORTS': 'Infrastructure',
    'TITAN': 'Retail', 'TRENT': 'Retail', 'NYKAA': 'Retail',
    'ZOMATO': 'Technology', 'PAYTM': 'Technology', 'POLICYBZR': 'Technology',
}

company_count = 0
company_errors = 0

for _, row in companies_df.iterrows():
    symbol = str(row['id']).strip().upper()
    company_name = str(row['company_name']).strip() if pd.notna(row.get('company_name')) else symbol

    # Determine sector
    sector = row.get('sector', None)
    if pd.isna(sector) if isinstance(sector, float) else (sector is None):
        sector = sector_map.get(symbol, 'Other')

    # Use roe_percentage as ROE, roce_percentage as a proxy for health_score
    roe_val    = safe_float(row, 'roe_percentage', default=0.0)
    roce_val   = safe_float(row, 'roce_percentage', default=0.0)
    # health_score: simple composite (capped 0-100)
    health     = min(max(round((roe_val + roce_val) / 2, 1), 0), 100)

    try:
        Company.objects.update_or_create(
            symbol=symbol,
            defaults={
                'company_name':   company_name,
                'sector':         sector if sector else 'Other',
                'health_score':   health,
                'roe':            roe_val,
                'opm':            0.0,       # will be filled from P&L below
                'debt_to_equity': 0.0,       # will be filled from balance sheet below
                'revenue_growth': 0.0,       # will be filled from P&L below
            }
        )
        company_count += 1
    except Exception as e:
        print(f"  [ERROR] Company {symbol}: {e}")
        company_errors += 1

print(f"[OK] Companies loaded: {company_count} | Errors: {company_errors}\n")

# ─────────────────────────────────────────────
# STEP 2: Load FinancialData from P&L
# ─────────────────────────────────────────────
pnl_df = pd.read_csv(PROCESSED_DIR / "profitandloss_clean.csv")
print(f"P&L rows to load: {len(pnl_df)}")

fin_count = 0
fin_errors = 0
opm_totals = {}   # symbol -> list of opm values (to update Company.opm later)

for _, row in pnl_df.iterrows():
    symbol = str(row['company_id']).strip().upper()
    year_raw = str(row.get('year', '')).strip()

    # Extract numeric year (e.g. "Mar 2022" -> 2022, "Dec 2021" -> 2021)
    year_digits = ''.join(filter(str.isdigit, year_raw))
    if not year_digits or len(year_digits) < 4:
        continue
    year = int(year_digits[-4:])

    try:
        company = Company.objects.get(symbol=symbol)
    except Company.DoesNotExist:
        continue

    sales      = safe_int(row, 'sales')
    net_profit = safe_int(row, 'net_profit')
    opm_pct    = safe_float(row, 'opm_percentage')
    eps        = safe_float(row, 'eps')

    # Collect OPM for later company-level update
    if symbol not in opm_totals:
        opm_totals[symbol] = []
    opm_totals[symbol].append(opm_pct)

    try:
        FinancialData.objects.update_or_create(
            company=company,
            year=year,
            defaults={
                'sales':      sales,
                'net_profit': net_profit,
                'opm_pct':    opm_pct,
                'eps':        eps,
            }
        )
        fin_count += 1
    except Exception as e:
        print(f"  [ERROR] FinancialData {symbol} {year}: {e}")
        fin_errors += 1

print(f"[OK] FinancialData loaded: {fin_count} | Errors: {fin_errors}\n")

# ─────────────────────────────────────────────
# STEP 3: Update Company.opm with avg OPM from P&L
# ─────────────────────────────────────────────
opm_updated = 0
for symbol, opm_list in opm_totals.items():
    valid = [x for x in opm_list if x != 0]
    if valid:
        avg_opm = round(sum(valid) / len(valid), 2)
        Company.objects.filter(symbol=symbol).update(opm=avg_opm)
        opm_updated += 1

print(f"[OK] OPM updated for {opm_updated} companies\n")

# ─────────────────────────────────────────────
# STEP 4: Update Company.debt_to_equity from Balance Sheet
# ─────────────────────────────────────────────
try:
    bs_df = pd.read_csv(PROCESSED_DIR / "balancesheet_clean.csv")
    de_updated = 0

    for symbol in Company.objects.values_list('symbol', flat=True):
        company_bs = bs_df[bs_df['company_id'].str.upper() == symbol]
        if company_bs.empty:
            continue
        # Use the most recent year
        latest = company_bs.sort_values('year', ascending=False).iloc[0]
        borrowings = safe_float(latest, 'borrowings')
        equity     = safe_float(latest, 'equity_capital') + safe_float(latest, 'reserves')
        if equity > 0:
            de = round(borrowings / equity, 2)
            Company.objects.filter(symbol=symbol).update(debt_to_equity=de)
            de_updated += 1

    print(f"[OK] Debt-to-Equity updated for {de_updated} companies\n")
except Exception as e:
    print(f"[WARN] Could not update D/E: {e}\n")

# ─────────────────────────────────────────────
# STEP 5: Summary
# ─────────────────────────────────────────────
total_companies = Company.objects.count()
total_financials = FinancialData.objects.count()

print("=" * 50)
print(f"[DONE] Database load complete!")
print(f"  Companies in DB  : {total_companies}")
print(f"  FinancialData rows: {total_financials}")
print("=" * 50)

print("\nSample companies in database:")
for c in Company.objects.all().order_by('symbol')[:8]:
    print(f"  {c.symbol:<15} | {c.company_name:<35} | Sector: {c.sector:<12} | Score: {c.health_score} | OPM: {c.opm}%")
