# apps/reports/views.py
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from weasyprint import HTML
from datetime import datetime

from apps.fuel.models import FuelRecord
from apps.trips.models import Trip
from .utils import get_date_range_from_request, get_fuel_summary, get_trip_summary

@login_required
def report_selector(request):
    """Página para escolher o tipo de relatório e período."""
    context = {
        'vehicles': None,  # Você pode passar lista de veículos para filtro
    }
    return render(request, 'reports/report_selector.html', context)

@login_required
def fuel_report_pdf(request):
    """Gera PDF do relatório de combustível (versão melhorada)."""
    start_date, end_date = get_date_range_from_request(request)
    vehicle_id = request.GET.get('vehicle')
    
    summary = get_fuel_summary(start_date, end_date, vehicle_id)
    
    # Renderiza o HTML do relatório
    html_string = render_to_string('reports/fuel_report.html', {
        'summary': summary,
        'generated_at': datetime.now(),
    })
    
    # Gera PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()
    
    # Resposta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"relatorio_combustivel_{start_date}_{end_date}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response

@login_required
def trip_report_pdf(request):
    """Gera PDF do relatório de viagens."""
    start_date, end_date = get_date_range_from_request(request)
    vehicle_id = request.GET.get('vehicle')
    
    summary = get_trip_summary(start_date, end_date, vehicle_id)
    
    html_string = render_to_string('reports/trip_report.html', {
        'summary': summary,
        'generated_at': datetime.now(),
    })
    
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f"relatorio_viagens_{start_date}_{end_date}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response