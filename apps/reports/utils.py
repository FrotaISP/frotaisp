# apps/reports/utils.py
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q
from apps.fuel.models import FuelRecord
from apps.trips.models import Trip
from apps.maintenance.models import Maintenance

def get_date_range_from_request(request):
    """Extrai start_date e end_date dos parâmetros GET, com fallback para últimos 30 dias."""
    start_str = request.GET.get('start_date')
    end_str = request.GET.get('end_date')
    today = timezone.now().date()
    
    if start_str and end_str:
        try:
            start_date = timezone.datetime.strptime(start_str, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = today - timedelta(days=30)
            end_date = today
    else:
        start_date = today - timedelta(days=30)
        end_date = today
    
    return start_date, end_date

def get_fuel_summary(start_date, end_date, vehicle_id=None):
    """Retorna resumo de combustível no período."""
    queryset = FuelRecord.objects.filter(date__range=[start_date, end_date])
    if vehicle_id:
        queryset = queryset.filter(vehicle_id=vehicle_id)
    
    aggregates = queryset.aggregate(
        total_liters=Sum('liters'),
        total_cost=Sum('total_cost'),
        count=Count('id')
    )
    
    records = queryset.select_related('vehicle').order_by('-date')
    
    return {
        'total_liters': aggregates['total_liters'] or 0,
        'total_cost': aggregates['total_cost'] or 0,
        'count': aggregates['count'] or 0,
        'records': records,
        'start_date': start_date,
        'end_date': end_date,
    }

def get_trip_summary(start_date, end_date, vehicle_id=None):
    """Retorna resumo de viagens no período."""
    queryset = Trip.objects.filter(start_time__date__gte=start_date, start_time__date__lte=end_date)
    if vehicle_id:
        queryset = queryset.filter(vehicle_id=vehicle_id)
    
    total_km = 0
    for trip in queryset:
        total_km += trip.distance()
    
    return {
        'total_trips': queryset.count(),
        'total_km': total_km,
        'trips': queryset.select_related('vehicle', 'driver').order_by('-start_time'),
        'start_date': start_date,
        'end_date': end_date,
    }