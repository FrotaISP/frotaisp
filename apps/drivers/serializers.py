# apps/drivers/serializers.py
from rest_framework import serializers
from .models import Driver

class DriverSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Driver
        fields = '__all__'

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username