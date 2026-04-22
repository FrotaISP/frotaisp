# apps/dashboard/views.py
from django.shortcuts import render
from django.db.models import Sum, Q, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required

from apps.core.mixins import scope_queryset_for_user
from apps.vehicles.models import Vehicle, VehicleChecklist, VehicleDocument
from apps.drivers.models import Driver
from apps.trips.models import Trip
from apps.fuel.models import FuelRecord
from apps.maintenance.models import Maintenance, PreventiveMaintenancePlan


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
    documents_qs = scope_queryset_for_user(VehicleDocument.objects.filter(is_active=True), request.user)
    checklists_qs = scope_queryset_for_user(VehicleChecklist.objects.all(), request.user)
    plans_qs = scope_queryset_for_user(PreventiveMaintenancePlan.objects.filter(status='active'), request.user)

    total_vehicles = vehicles_qs.filter(is_active=True).count()
    available_drivers = drivers_qs.filter(is_available=True).count()
    drivers_in_trip = trips_qs.filter(end_time__isnull=True).count()

    month_trips = trips_qs.filter(start_time__date__gte=first_day_of_month, end_odometer__isnull=False)
    month_km = sum(trip.distance() for trip in month_trips)

    fuel_30 = fuel_qs.filter(date__gte=last_30_days)
    maintenance_30 = maintenance_qs.filter(date__gte=last_30_days)
    total_fuel_cost = fuel_30.aggregate(total=Sum('total_cost'))['total'] or 0
    total_maintenance_cost = maintenance_30.aggregate(total=Sum('cost'))['total'] or 0
    trips_30 = trips_qs.filter(start_time__date__gte=last_30_days, end_odometer__isnull=False)
    total_km_30 = sum(trip.distance() for trip in trips_30)
    avg_cost_per_km = (total_fuel_cost + total_maintenance_cost) / total_km_30 if total_km_30 > 0 else 0

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
        alerts.append({'type': 'maintenance', 'vehicle': maint.vehicle, 'message': f"Manutencao {maint.get_type_display().lower()} proxima", 'urgency': 'warning'})

    for plan in plans_qs.select_related('vehicle'):
        if plan.is_overdue or plan.is_due_soon:
            alerts.append({'type': 'plan', 'vehicle': plan.vehicle, 'message': f"Preventiva: {plan.service_name}", 'urgency': 'danger' if plan.is_overdue else 'warning'})

    for doc in documents_qs.select_related('vehicle', 'driver', 'driver__user'):
        if doc.is_expired or doc.is_expiring_soon:
            target = doc.vehicle or doc.driver
            alerts.append({'type': 'document', 'target': target, 'message': f"Documento {doc.title} vence em {doc.days_until_expiration} dias", 'urgency': 'danger' if doc.is_expired else 'warning'})

    for checklist in checklists_qs.filter(status__in=['attention', 'blocked']).select_related('vehicle')[:5]:
        alerts.append({'type': 'checklist', 'vehicle': checklist.vehicle, 'message': f"Checklist {checklist.get_status_display().lower()}", 'urgency': 'danger' if checklist.status == 'blocked' else 'warning'})

    for driver in drivers_qs.filter(cnh_expiration__lte=today + timedelta(days=30)).select_related('user'):
        days_left = (driver.cnh_expiration - today).days
        urgency = 'danger' if days_left <= 7 else 'warning'
        alerts.append({'type': 'cnh', 'driver': driver, 'message': f"CNH de {driver.user.get_full_name()} vence em {days_left} dias", 'urgency': urgency})

    vehicles_data = []
    for vehicle in vehicles:
        vehicles_data.append({
            'vehicle': vehicle,
            'active_driver': vehicle.current_driver,
            'in_trip': trips_qs.filter(vehicle=vehicle, end_time__isnull=True).exists(),
            'fuel_pct': None,
        })

    context = {
        'total_vehicles': total_vehicles,
        'available_drivers': available_drivers,
        'drivers_in_trip': drivers_in_trip,
        'month_km': month_km,
        'avg_cost_per_km': avg_cost_per_km,
        'open_preventive_count': sum(1 for plan in plans_qs if plan.is_overdue or plan.is_due_soon),
        'expiring_documents_count': sum(1 for doc in documents_qs if doc.is_expired or doc.is_expiring_soon),
        'checklist_issues_count': checklists_qs.filter(status__in=['attention', 'blocked']).count(),
        'consumption_labels': consumption_labels,
        'consumption_data': consumption_data,
        'vehicles': vehicles,
        'vehicles_data': vehicles_data,
        'alerts': alerts[:8],
    }
    return render(request, 'dashboard/index.html', context)
