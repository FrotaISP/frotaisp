# apps/dashboard/views.py
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import timedelta

from apps.core.mixins import get_user_profile, scope_queryset_for_user
from apps.vehicles.models import Tire, Vehicle, VehicleChecklist, VehicleDocument
from apps.drivers.models import Driver
from apps.trips.models import Trip
from apps.fuel.models import FuelRecord
from apps.maintenance.models import Maintenance, PreventiveMaintenancePlan, VehicleExpense, WorkOrder
from apps.mobile_api.models import MobileOccurrence


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
    tires_qs = scope_queryset_for_user(Tire.objects.all(), request.user)
    work_orders_qs = scope_queryset_for_user(WorkOrder.objects.all(), request.user)
    expenses_qs = scope_queryset_for_user(VehicleExpense.objects.all(), request.user)
    occurrences_qs = scope_queryset_for_user(MobileOccurrence.objects.all(), request.user)

    total_vehicles = vehicles_qs.filter(is_active=True).count()
    available_drivers = drivers_qs.filter(is_available=True).count()
    drivers_in_trip = trips_qs.filter(end_time__isnull=True).count()

    month_trips = trips_qs.filter(start_time__date__gte=first_day_of_month, end_odometer__isnull=False)
    month_km = sum(trip.distance() for trip in month_trips)

    fuel_30 = fuel_qs.filter(date__gte=last_30_days)
    maintenance_30 = maintenance_qs.filter(date__gte=last_30_days)
    expenses_month = expenses_qs.filter(date__gte=first_day_of_month)
    total_fuel_cost = fuel_30.aggregate(total=Sum('total_cost'))['total'] or 0
    total_maintenance_cost = maintenance_30.aggregate(total=Sum('cost'))['total'] or 0
    total_expense_month = expenses_month.aggregate(total=Sum('amount'))['total'] or 0
    trips_30 = trips_qs.filter(start_time__date__gte=last_30_days, end_odometer__isnull=False)
    total_km_30 = sum(trip.distance() for trip in trips_30)
    avg_cost_per_km = (total_fuel_cost + total_maintenance_cost + total_expense_month) / total_km_30 if total_km_30 > 0 else 0

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
        alerts.append({'type': 'maintenance', 'label': maint.vehicle.plate, 'message': f"Manutencao {maint.get_type_display().lower()} proxima", 'urgency': 'warning'})

    plans_due_count = 0
    for plan in plans_qs.select_related('vehicle'):
        if plan.is_overdue or plan.is_due_soon:
            plans_due_count += 1
            alerts.append({'type': 'plan', 'label': plan.vehicle.plate, 'message': f"Preventiva: {plan.service_name}", 'urgency': 'danger' if plan.is_overdue else 'warning'})

    documents_due_count = 0
    for doc in documents_qs.select_related('vehicle', 'driver', 'driver__user'):
        if doc.is_expired or doc.is_expiring_soon:
            documents_due_count += 1
            target = doc.vehicle or doc.driver
            message = f"Documento {doc.title} vencido" if doc.is_expired else f"Documento {doc.title} vence em {doc.days_until_expiration} dias"
            alerts.append({'type': 'document', 'label': str(target), 'message': message, 'urgency': 'danger' if doc.is_expired else 'warning'})

    for checklist in checklists_qs.filter(status__in=['attention', 'blocked']).select_related('vehicle')[:5]:
        alerts.append({'type': 'checklist', 'label': checklist.vehicle.plate, 'message': f"Checklist {checklist.get_status_display().lower()}", 'urgency': 'danger' if checklist.status == 'blocked' else 'warning'})

    for order in work_orders_qs.filter(status__in=['open', 'scheduled', 'in_progress', 'waiting_parts']).select_related('vehicle')[:5]:
        if order.priority in ('high', 'critical') or (order.scheduled_date and order.scheduled_date < today):
            alerts.append({'type': 'work_order', 'label': order.vehicle.plate, 'message': f"OS #{order.pk}: {order.title}", 'urgency': 'danger' if order.priority == 'critical' else 'warning'})

    for driver in drivers_qs.filter(cnh_expiration__lte=today + timedelta(days=30)).select_related('user'):
        days_left = (driver.cnh_expiration - today).days
        urgency = 'danger' if days_left <= 7 else 'warning'
        alerts.append({'type': 'cnh', 'label': driver.user.get_full_name() or driver.user.username, 'message': f"CNH vence em {days_left} dias", 'urgency': urgency})

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
        'open_preventive_count': plans_due_count,
        'expiring_documents_count': documents_due_count,
        'checklist_issues_count': checklists_qs.filter(status__in=['attention', 'blocked']).count(),
        'open_work_orders_count': work_orders_qs.filter(status__in=['open', 'scheduled', 'in_progress', 'waiting_parts']).count(),
        'tires_attention_count': tires_qs.filter(Q(status__in=['repair', 'retread']) | Q(current_tread_mm__lte=3)).count(),
        'total_expense_month': total_expense_month,
        'consumption_labels': consumption_labels,
        'consumption_data': consumption_data,
        'vehicles': vehicles,
        'vehicles_data': vehicles_data,
        'alerts': alerts[:8],
        'open_occurrences_count': occurrences_qs.filter(status__in=['open', 'in_progress']).count(),
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def tracking_map_view(request):
    vehicles_qs = scope_queryset_for_user(Vehicle.objects.filter(is_active=True), request.user)
    smartphone_count = vehicles_qs.filter(location_source__icontains='app_mobile').count()
    context = {
        'tracked_count': vehicles_qs.filter(latitude__isnull=False, longitude__isnull=False).count(),
        'total_active_count': vehicles_qs.count(),
        'smartphone_count': smartphone_count,
    }
    return render(request, 'dashboard/tracking_map.html', context)


@login_required
def tracking_positions_api(request):
    vehicles_qs = scope_queryset_for_user(
        Vehicle.objects.filter(is_active=True).select_related('current_driver', 'current_driver__user'),
        request.user,
    )
    active_trip_vehicle_ids = set(
        scope_queryset_for_user(Trip.objects.filter(end_time__isnull=True), request.user)
        .values_list('vehicle_id', flat=True)
    )
    vehicles = []
    for vehicle in vehicles_qs.order_by('plate'):
        last_location_at = vehicle.last_location_at
        vehicles.append({
            'id': vehicle.id,
            'plate': vehicle.plate,
            'model': vehicle.model,
            'brand': vehicle.brand,
            'driver': str(vehicle.current_driver) if vehicle.current_driver_id else '',
            'driver_id': vehicle.current_driver_id,
            'latitude': float(vehicle.latitude) if vehicle.latitude is not None else None,
            'longitude': float(vehicle.longitude) if vehicle.longitude is not None else None,
            'speed': float(vehicle.last_speed_kmh) if vehicle.last_speed_kmh is not None else None,
            'heading': vehicle.heading_degrees,
            'status': vehicle.tracking_status,
            'in_trip': vehicle.id in active_trip_vehicle_ids,
            'odometer': vehicle.current_odometer,
            'source': vehicle.location_source,
            'is_smartphone_source': bool(vehicle.location_source and 'app_mobile' in vehicle.location_source),
            'last_location_at': last_location_at.isoformat() if last_location_at else None,
            'last_location_display': timezone.localtime(last_location_at).strftime('%d/%m/%Y %H:%M:%S') if last_location_at else 'Sem posicao',
        })
    return JsonResponse({'vehicles': vehicles, 'updated_at': timezone.now().isoformat()})


@login_required
def occurrences_view(request):
    profile = get_user_profile(request.user)
    if not profile.is_manager:
        messages.error(request, 'Apenas gestores podem acompanhar ocorrencias.')
        return redirect('dashboard:index')

    base_items = scope_queryset_for_user(
        MobileOccurrence.objects.select_related('driver__user', 'vehicle').all(),
        request.user,
    )
    items = base_items

    severity = request.GET.get('severity', '').strip()
    status_filter = request.GET.get('status', '').strip()
    category = request.GET.get('category', '').strip()
    if severity:
        items = items.filter(severity=severity)
    if status_filter:
        items = items.filter(status=status_filter)
    if category:
        items = items.filter(category=category)

    context = {
        'occurrences': items.order_by('-reported_at', '-created_at')[:100],
        'selected_severity': severity,
        'selected_status': status_filter,
        'selected_category': category,
        'occurrences_total': base_items.count(),
        'occurrences_open': base_items.filter(status='open').count(),
        'occurrences_in_progress': base_items.filter(status='in_progress').count(),
        'occurrences_resolved': base_items.filter(status='resolved').count(),
    }
    return render(request, 'dashboard/occurrences.html', context)


@login_required
def occurrence_status_update_view(request, pk):
    profile = get_user_profile(request.user)
    if not profile.is_manager:
        messages.error(request, 'Apenas gestores podem atualizar ocorrencias.')
        return redirect('dashboard:index')
    if request.method != 'POST':
        return redirect('dashboard:occurrences')

    occurrence = get_object_or_404(
        scope_queryset_for_user(MobileOccurrence.objects.all(), request.user),
        pk=pk,
    )
    new_status = request.POST.get('status', '').strip()
    allowed = {'open', 'in_progress', 'resolved'}
    if new_status not in allowed:
        messages.error(request, 'Status invalido para ocorrencia.')
        return redirect('dashboard:occurrences')

    occurrence.status = new_status
    occurrence.save(update_fields=['status', 'updated_at'])
    messages.success(request, 'Status da ocorrencia atualizado com sucesso.')
    return redirect('dashboard:occurrences')
