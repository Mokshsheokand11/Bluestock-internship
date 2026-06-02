from api.models import Company

# Sample Nifty 100 Companies
companies = [
    {"symbol": "TCS", "company_name": "Tata Consultancy Services", "sector": "IT", "health_score": 92, "roe": 28.5, "opm": 26.2, "debt_to_equity": 0.08, "revenue_growth": 11.2},
    {"symbol": "HDFCBANK", "company_name": "HDFC Bank Ltd", "sector": "Banking", "health_score": 88, "roe": 17.8, "opm": 0, "debt_to_equity": 0.12, "revenue_growth": 14.5},
    {"symbol": "INFY", "company_name": "Infosys Ltd", "sector": "IT", "health_score": 85, "roe": 24.1, "opm": 22.8, "debt_to_equity": 0.05, "revenue_growth": 9.8},
    {"symbol": "RELIANCE", "company_name": "Reliance Industries", "sector": "Energy", "health_score": 79, "roe": 8.2, "opm": 12.4, "debt_to_equity": 0.45, "revenue_growth": 7.5},
    {"symbol": "ICICIBANK", "company_name": "ICICI Bank Ltd", "sector": "Banking", "health_score": 82, "roe": 16.9, "opm": 0, "debt_to_equity": 0.18, "revenue_growth": 18.2},
]

for c in companies:
    Company.objects.get_or_create(symbol=c["symbol"], defaults=c)

print("Sample data added successfully!")
