from decimal import Decimal

from django.test import TestCase

from apps.maintenance.models import Maintenance
from apps.vehicles.models import Vehicle


class MaintenanceModelTests(TestCase):
    def test_save_updates_vehicle_current_odometer(self):
        vehicle = Vehicle.objects.create(
            plate='GHI9012',
            brand='Chevrolet',
            model='Montana',
            year=2022,
            fuel_type='D',
            current_odometer=3000,
        )

        Maintenance.objects.create(
            vehicle=vehicle,
            type='P',
            date='2026-04-22',
            description='Troca de oleo',
            cost=Decimal('350.00'),
            odometer=3400,
            workshop='Oficina Sul',
        )

        vehicle.refresh_from_db()
        self.assertEqual(vehicle.current_odometer, 3400)
