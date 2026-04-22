# apps/drivers/api/views.py
from rest_framework import viewsets
from apps.drivers.models import Driver
from apps.drivers.serializers import DriverSerializer

class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.filter(is_available=True)
    serializer_class = DriverSerializer