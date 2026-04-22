# apps/dashboard/views.py
from django.shortcuts import render
from django.db.models import Sum, Q, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required

from apps.core.mixins import scope_queryset_for_user
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

    vehicles_qs = scope_queryset_for_user(Vehicle.objects.all(), request.user)
    drivers_qs = scope_queryset_for_user(Driver.objects.all(), request.user)
    trips_qs = scope_queryset_for_user(Trip.objects.all(), request.user)
    fuel_qs = scope_queryset_for_user(FuelRecord.objects.all(), request.user)
    maintenance_qs = scope_queryset_for_user(Maintenance.objects.all(), request.user)

    total_vehicles = vehicles_qs.filter(is_active=True).count()
    available_drivers = drivers_qs.filter(is_available=True).count()
    drivers_in_trip = trips_qs.filter(end_time__isnull=True).count()

    month_trips = trips_qs.filter(start_time__date__gte=first_day_of_month, end_odometer__isnull=False)
    month_km = sum(trip.distance() for trip in month_trips)

    fuel_30 = fuel_qs.filter(date__gte=last_30_days)
    total_fuel_cost = fuel_30.aggregate(total=Sum('total_cost'))['total'] or 0
    trips_30 = trips_qs.filter(start_time__date__gte=last_30_days, end_odometer__isnull=False)
    total_km_30 = sum(trip.distance() for trip in trips_30)
    avg_cost_per_km = total_fuel_cost / total_km_30 if total_km_30 > 0 else 0

    consumption_labels = []
    consumption_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_total = fuel_qs.filter(date=day).aggregate(total=Sum('liters'))['total'] or 0
        consumption_labels.append(day.strftime('%a'))
        consumption_data.append(float(day_total))

    vehicles = vehicles_qs.filter(is_active=True).select_related('current_driver').order_by('plate')[:10]

    alerts = []
    for maint in maintenance_qs.filter(
        Q(next_alert_km__lte=F('vehicle__current_odometer') + 500) |
        Q(next_alert_date__lte=today + timedelta(days=7))
    ).select_related('vehicle'):
        alerts.append({
            'type': 'maintenance',
            'vehicle': maint.vehicle,
            'message': f"Manutencao {maint.get_type_display().lower()} proxima",
            'urgency': 'warning',
        })

    for driver in drivers_qs.filter(cnh_expiration__lte=today + timedelta(days=30)).select_related('user'):
        days_left = (driver.cnh_expiration - today).days
        urgency = 'danger' if days_left <= 7 else 'warning'
        alerts.append({
            'type': 'cnh',
            'driver': driver,
            'message': f"CNH de {driver.user.get_full_name()} vence em {days_left} dias",
            'urgency': urgency,
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
        'alerts': alerts[:5],
    }
    return render(request, 'dashboard/index.html', context)
