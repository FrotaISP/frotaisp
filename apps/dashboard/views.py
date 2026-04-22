# apps/dashboard/views.py
# apps/dashboard/views.py
from django.shortcuts import render
from django.db.models import Sum, Q, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required

from apps.vehicles.models import Vehicle
from apps.drivers.models import Driver
from apps.trips.models import Trip
from apps.fuel.models import FuelRecord
from apps.maintenance.models import Maintenance

@login_required
def dashboard_view(request):
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    last_30_days = today - timedelta(days=30)

    # Cards de resumo
    total_vehicles = Vehicle.objects.filter(is_active=True).count()
    available_drivers = Driver.objects.filter(is_available=True).count()
    drivers_in_trip = Trip.objects.filter(end_time__isnull=True).count()

    # Km do mês atual
    month_trips = Trip.objects.filter(
        start_time__date__gte=first_day_of_month,
        end_odometer__isnull=False
    )
    month_km = 0
    for trip in month_trips:
        month_km += trip.distance()

    # Custo médio por km (últimos 30 dias)
    fuel_30 = FuelRecord.objects.filter(date__gte=last_30_days)
    total_fuel_cost = fuel_30.aggregate(total=Sum('total_cost'))['total'] or 0
    total_km_30 = 0
    trips_30 = Trip.objects.filter(start_time__date__gte=last_30_days, end_odometer__isnull=False)
    for trip in trips_30:
        total_km_30 += trip.distance()
    avg_cost_per_km = total_fuel_cost / total_km_30 if total_km_30 > 0 else 0

    # Consumo de combustível últimos 7 dias (para gráfico)
    consumption_labels = []
    consumption_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_total = FuelRecord.objects.filter(date=day).aggregate(total=Sum('liters'))['total'] or 0
        consumption_labels.append(day.strftime('%a'))  # Ex: 'Mon', 'Tue'...
        consumption_data.append(float(day_total))

    # Veículos para tabela (últimos 10 ativos)
    vehicles = Vehicle.objects.filter(is_active=True).select_related('current_driver').order_by('plate')[:10]

    # Alertas
    alerts = []
    # Manutenções próximas (km ou data)
    for maint in Maintenance.objects.filter(
        Q(next_alert_km__lte=F('vehicle__current_odometer') + 500) |
        Q(next_alert_date__lte=today + timedelta(days=7))
    ).select_related('vehicle'):
        alerts.append({
            'type': 'maintenance',
            'vehicle': maint.vehicle,
            'message': f"Manutenção {maint.get_type_display().lower()} próxima",
            'urgency': 'warning'
        })
    # CNH a vencer em até 30 dias
    for driver in Driver.objects.filter(cnh_expiration__lte=today + timedelta(days=30)).select_related('user'):
        days_left = (driver.cnh_expiration - today).days
        urgency = 'danger' if days_left <= 7 else 'warning'
        alerts.append({
            'type': 'cnh',
            'driver': driver,
            'message': f"CNH de {driver.user.get_full_name()} vence em {days_left} dias",
            'urgency': urgency
        })

    context = {
        'total_vehicles': total_vehicles,
        'available_drivers': available_drivers,
        'drivers_in_trip': drivers_in_trip,
        'month_km': month_km,
        'avg_cost_per_km': avg_cost_per_km,
        'consumption_labels': consumption_labels,
        'consumption_data': consumption_data,
        'vehicles': vehicles,
        'alerts': alerts[:5],  # limita a 5 alertas
    }
    return render(request, 'dashboard/index.html', context)