from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),           # Frontend loads here
    path('companies/', views.company_list, name='company_list'),
    path('companies/<str:symbol>/', views.company_detail, name='company_detail'),
    path('health-leaderboard/', views.health_leaderboard, name='health_leaderboard'),
]
