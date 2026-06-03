from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Company

@api_view(['GET'])
def company_list(request):
    companies = Company.objects.all().order_by('-health_score')
    data = []
    for c in companies:
        data.append({
            'symbol': c.symbol,
            'company_name': c.company_name,
            'sector': c.sector,
            'health_score': c.health_score,
            'health_label': c.health_label,
            'roe': round(c.roe, 2) if c.roe else 0,
            'opm': round(c.opm, 2) if c.opm else 0,
            'debt_to_equity': round(c.debt_to_equity, 2) if c.debt_to_equity else 0,
            'revenue_growth': round(c.revenue_growth, 2) if c.revenue_growth else 0,
        })
    return Response(data)

@api_view(['GET'])
def company_detail(request, symbol):
    try:
        c = Company.objects.get(symbol=symbol)
        return Response({
            'symbol': c.symbol,
            'company_name': c.company_name,
            'sector': c.sector,
            'health_score': c.health_score,
            'health_label': c.health_label,
            'roe': round(c.roe, 2) if c.roe else 0,
            'opm': round(c.opm, 2) if c.opm else 0,
            'debt_to_equity': round(c.debt_to_equity, 2) if c.debt_to_equity else 0,
            'revenue_growth': round(c.revenue_growth, 2) if c.revenue_growth else 0,
        })
    except Company.DoesNotExist:
        return Response({"error": "Company not found"}, status=404)