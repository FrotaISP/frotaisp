# apps/vehicles/api/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.core.mixins import get_user_company, scope_queryset_for_user
from apps.vehicles.models import Vehicle
from apps.vehicles.serializers import VehicleSerializer


class VehicleViewSet(viewsets.ModelViewSet):
    serializer_class = VehicleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return scope_queryset_for_user(Vehicle.objects.filter(is_active=True), self.request.user)

    def perform_create(self, serializer):
        serializer.save(company=get_user_company(self.request.user))
