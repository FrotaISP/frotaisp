# apps/fuel/serializers.py
from rest_framework import serializers
from .models import FuelRecord

class FuelRecordSerializer(serializers.ModelSerializer):
    vehicle_plate = serializers.CharField(source='vehicle.plate', read_only=True)

    class Meta:
        model = FuelRecord
        fields = '__all__'