from decimal import Decimal

from django.test import TestCase

from apps.fuel.models import FuelRecord
from apps.vehicles.models import Vehicle


class FuelRecordModelTests(TestCase):
    def test_save_updates_vehicle_current_odometer(self):
        vehicle = Vehicle.objects.create(
            plate='DEF5678',
            brand='Volkswagen',
            model='Saveiro',
            year=2023,
            fuel_type='G',
            current_odometer=2000,
        )

        FuelRecord.objects.create(
            vehicle=vehicle,
            date='2026-04-22',
            liters=Decimal('42.50'),
            price_per_liter=Decimal('5.89'),
            odometer=2300,
            gas_station='Posto Centro',
        )

        vehicle.refresh_from_db()
        self.assertEqual(vehicle.current_odometer, 2300)
