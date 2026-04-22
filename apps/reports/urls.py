from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Painel geral de relatórios
    path('', views.ReportsDashboardView.as_view(), name='dashboard'),

    # ── Combustível ──────────────────────────────────────────────
    path('combustivel/', views.FuelReportView.as_view(), name='fuel'),
    path('combustivel/pdf/', views.FuelReportPDFView.as_view(), name='fuel_pdf'),
    path('combustivel/excel/', views.FuelReportExcelView.as_view(), name='fuel_excel'),

    # ── Viagens ──────────────────────────────────────────────────
    path('viagens/', views.TripReportView.as_view(), name='trips'),
    path('viagens/pdf/', views.TripReportPDFView.as_view(), name='trips_pdf'),
    path('viagens/excel/', views.TripReportExcelView.as_view(), name='trips_excel'),

    # ── Manutenção ───────────────────────────────────────────────
    path('manutencao/', views.MaintenanceReportView.as_view(), name='maintenance'),
    path('manutencao/pdf/', views.MaintenanceReportPDFView.as_view(), name='maintenance_pdf'),
    path('manutencao/excel/', views.MaintenanceReportExcelView.as_view(), name='maintenance_excel'),

    # ── Relatório Geral ──────────────────────────────────────────
    path('geral/', views.GeneralReportView.as_view(), name='general'),
    path('geral/pdf/', views.GeneralReportPDFView.as_view(), name='general_pdf'),
    path('geral/excel/', views.GeneralReportExcelView.as_view(), name='general_excel'),
]
