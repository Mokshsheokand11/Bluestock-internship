from django.urls import path
from . import views

urlpatterns = [
    path('', views.company_list, name='home'),
    path('companies/', views.company_list, name='company_list'),
    path('companies/<str:symbol>/', views.company_detail, name='company_detail'),
]