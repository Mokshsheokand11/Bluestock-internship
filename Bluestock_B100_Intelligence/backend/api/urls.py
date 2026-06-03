from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    # Professional Frontend at root
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    
    # API endpoints
    path('api/companies/', views.company_list, name='company_list'),
    path('api/companies/<str:symbol>/', views.company_detail, name='company_detail'),
]