# apps/reports/urls.py
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_selector, name='selector'),
    path('combustivel/pdf/', views.fuel_report_pdf, name='fuel_pdf'),
    path('viagens/pdf/', views.trip_report_pdf, name='trip_pdf'),
    # Futuramente: path('excel/...')
]