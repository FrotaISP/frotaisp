# apps/vehicles/api/views.py
from rest_framework import viewsets
from apps.vehicles.models import Vehicle
from apps.vehicles.serializers import VehicleSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.filter(is_active=True)
    serializer_class = VehicleSerializer