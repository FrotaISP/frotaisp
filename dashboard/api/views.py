# apps/dashboard/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count

from apps.vehicles.models import Vehicle
from apps.drivers.models import Driver
from apps.trips.models import Trip
from apps.fuel.models import FuelRecord

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    today = timezone.now().date()
    first_day = today.replace(day=1)
    last_30 = today - timedelta(days=30)

    total_vehicles = Vehicle.objects.filter(is_active=True).count()
    available_drivers = Driver.objects.filter(is_available=True).count()
    drivers_in_trip = Trip.objects.filter(end_time__isnull=True).count()

    month_km = 0
    for trip in Trip.objects.filter(start_time__date__gte=first_day, end_odometer__isnull=False):
        month_km += trip.distance()

    fuel_cost = FuelRecord.objects.filter(date__gte=last_30).aggregate(total=Sum('total_cost'))['total'] or 0
    total_km_30 = 0
    for trip in Trip.objects.filter(start_time__date__gte=last_30, end_odometer__isnull=False):
        total_km_30 += trip.distance()
    avg_cost_per_km = fuel_cost / total_km_30 if total_km_30 else 0

    return Response({
        'total_vehicles': total_vehicles,
        'available_drivers': available_drivers,
        'drivers_in_trip': drivers_in_trip,
        'month_km': month_km,
        'avg_cost_per_km': round(avg_cost_per_km, 2),
    })