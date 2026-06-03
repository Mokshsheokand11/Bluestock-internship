"""
Health Scoring Script for Bluestock B100 Project
This script calculates Financial Health Score (0-100) for companies
and updates the Django database.
"""

import os
import django
import pandas as pd
from pathlib import Path

import sys
import io

# Fix Unicode output on Windows terminals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Setup Django
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.bluestock.settings')
django.setup()

from backend.api.models import Company

print("=" * 60)
print("🚀 STARTING FINANCIAL HEALTH SCORING")
print("=" * 60)

# Get all companies from database
companies = Company.objects.all()
print(f"Total companies to score: {companies.count()}\n")

updated_count = 0

for company in companies:
    try:
        # Get current values (with defaults if missing)
        roe = company.roe or 10
        opm = company.opm or 10
        de = company.debt_to_equity or 0.5
        rev_growth = company.revenue_growth or 5
        
        # ============================================
        # HEALTH SCORING LOGIC (Simplified but Good)
        # ============================================
        
        # 1. Profitability Score (ROE + OPM) - Max 25 points
        profitability = min((roe / 30) * 15 + (opm / 30) * 10, 25)
        
        # 2. Revenue Growth Score - Max 20 points
        if rev_growth > 20:
            growth_score = 20
        elif rev_growth > 10:
            growth_score = 15
        elif rev_growth > 5:
            growth_score = 10
        else:
            growth_score = 5
        
        # 3. Leverage Score (Lower D/E is better) - Max 20 points
        if de < 0.1:
            leverage_score = 20
        elif de < 0.3:
            leverage_score = 15
        elif de < 0.6:
            leverage_score = 10
        else:
            leverage_score = 5
        
        # 4. Cash Flow Quality (using OPM as proxy for now) - Max 15 points
        cashflow_score = min(opm / 2, 15)
        
        # 5. Dividend Track (placeholder - we don't have data yet) - Max 10 points
        dividend_score = 7  # Default medium score
        
        # 6. Growth Trend (using revenue growth as proxy) - Max 10 points
        trend_score = min(rev_growth / 2, 10)
        
        # Final Score (out of 100)
        final_score = round(
            profitability + 
            growth_score + 
            leverage_score + 
            cashflow_score + 
            dividend_score + 
            trend_score
        )
        
        # Make sure score is between 0 and 100
        final_score = max(0, min(100, final_score))
        
        # ============================================
        # Update the company in database
        # ============================================
        company.health_score = final_score
        company.save()
        
        updated_count += 1
        
        if updated_count <= 10:  # Show first 10 for preview
            print(f"{company.symbol:12} | Score: {final_score:5.1f} | ROE: {roe:6.2f} | D/E: {de:.2f}")
            
    except Exception as e:
        print(f"Error processing {company.symbol}: {e}")

print("\n" + "=" * 60)
print(f"✅ Health Scoring Completed!")
print(f"   Total companies updated: {updated_count}")
print("=" * 60)
