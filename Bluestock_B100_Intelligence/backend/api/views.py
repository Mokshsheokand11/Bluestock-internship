from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Company, FinancialData
from .serializers import CompanySerializer, FinancialDataSerializer

def home(request):
    return render(request, 'index.html')


@api_view(['GET'])
def company_list(request):
    companies = Company.objects.all()
    serializer = CompanySerializer(companies, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def company_detail(request, symbol):
    try:
        company = Company.objects.get(symbol=symbol)
        serializer = CompanySerializer(company)
        return Response(serializer.data)
    except Company.DoesNotExist:
        return Response({"error": "Company not found"}, status=404)


@api_view(['GET'])
def health_leaderboard(request):
    companies = Company.objects.order_by('-health_score')[:10]
    serializer = CompanySerializer(companies, many=True)
    return Response(serializer.data)
