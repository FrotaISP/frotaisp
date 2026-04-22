# apps/maintenance/serializers.py
from rest_framework import serializers
from .models import Maintenance

class MaintenanceSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(source='vehicle.plate', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Maintenance
        fields = '__all__'