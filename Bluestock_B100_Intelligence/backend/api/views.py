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
            'roe': c.roe,
            'opm': c.opm,
            'debt_to_equity': c.debt_to_equity,
            'revenue_growth': c.revenue_growth,
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
            'roe': c.roe,
            'opm': c.opm,
            'debt_to_equity': c.debt_to_equity,
            'revenue_growth': c.revenue_growth,
        })
    except Company.DoesNotExist:
        return Response({"error": "Company not found"}, status=404)