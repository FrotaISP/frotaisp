from datetime import timedelta
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from apps.fuel.forms import FuelRecordForm
from apps.fuel.models import FuelRecord
from apps.vehicles.models import Vehicle


class FuelRecordModelTests(TestCase):
    def setUp(self):
        self.vehicle = Vehicle.objects.create(
            plate='DEF5678',
            brand='Volkswagen',
            model='Saveiro',
            year=2023,
            fuel_type='G',
            current_odometer=2000,
        )

    def test_save_updates_vehicle_current_odometer(self):
        FuelRecord.objects.create(
            vehicle=self.vehicle,
            date='2026-04-22',
            liters=Decimal('42.50'),
            price_per_liter=Decimal('5.89'),
            odometer=2300,
            gas_station='Posto Centro',
        )

        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.current_odometer, 2300)


class FuelRecordFormTests(TestCase):
    def setUp(self):
        self.vehicle = Vehicle.objects.create(
            plate='QRS1234',
            brand='Fiat',
            model='Toro',
            year=2024,
            fuel_type='D',
            current_odometer=10000,
        )

    def build_form(self, **overrides):
        data = {
            'vehicle': self.vehicle.pk,
            'date': timezone.localdate().isoformat(),
            'liters': '40.00',
            'price_per_liter': '5.50',
            'odometer': 10100,
            'gas_station': 'Posto Norte',
        }
        data.update(overrides)
        return FuelRecordForm(data=data)

    def test_rejects_future_fuel_date(self):
        form = self.build_form(date=(timezone.localdate() + timedelta(days=1)).isoformat())

        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)

    def test_rejects_non_positive_liters(self):
        form = self.build_form(liters='0')

        self.assertFalse(form.is_valid())
        self.assertIn('liters', form.errors)

    def test_rejects_invalid_receipt_type(self):
        receipt = SimpleUploadedFile('receipt.exe', b'bad-file', content_type='application/octet-stream')
        form = FuelRecordForm(
            data={
                'vehicle': self.vehicle.pk,
                'date': timezone.localdate().isoformat(),
                'liters': '40.00',
                'price_per_liter': '5.50',
                'odometer': 10100,
                'gas_station': 'Posto Norte',
            },
            files={'receipt': receipt},
        )

        self.assertFalse(form.is_valid())
        self.assertIn('receipt', form.errors)

    def test_rejects_oversized_receipt(self):
        receipt = SimpleUploadedFile(
            'receipt.pdf',
            b'x' * (5 * 1024 * 1024 + 1),
            content_type='application/pdf',
        )
        form = FuelRecordForm(
            data={
                'vehicle': self.vehicle.pk,
                'date': timezone.localdate().isoformat(),
                'liters': '40.00',
                'price_per_liter': '5.50',
                'odometer': 10100,
                'gas_station': 'Posto Norte',
            },
            files={'receipt': receipt},
        )

        self.assertFalse(form.is_valid())
        self.assertIn('receipt', form.errors)
