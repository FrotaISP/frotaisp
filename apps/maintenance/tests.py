from datetime import timedelta
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from apps.maintenance.forms import MaintenanceForm
from apps.maintenance.models import Maintenance
from apps.vehicles.models import Vehicle


class MaintenanceModelTests(TestCase):
    def setUp(self):
        self.vehicle = Vehicle.objects.create(
            plate='GHI9012',
            brand='Chevrolet',
            model='Montana',
            year=2022,
            fuel_type='D',
            current_odometer=3000,
        )

    def test_save_updates_vehicle_current_odometer(self):
        Maintenance.objects.create(
            vehicle=self.vehicle,
            type='P',
            date='2026-04-22',
            description='Troca de oleo',
            cost=Decimal('350.00'),
            odometer=3400,
            workshop='Oficina Sul',
        )

        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.current_odometer, 3400)


class MaintenanceFormTests(TestCase):
    def setUp(self):
        self.vehicle = Vehicle.objects.create(
            plate='TUV5678',
            brand='Ford',
            model='Ranger',
            year=2024,
            fuel_type='D',
            current_odometer=8000,
        )

    def build_form(self, **overrides):
        data = {
            'vehicle': self.vehicle.pk,
            'type': 'P',
            'date': timezone.localdate().isoformat(),
            'description': 'Revisao preventiva',
            'cost': '450.00',
            'odometer': 8200,
            'workshop': 'Oficina Centro',
            'next_alert_km': 9000,
            'next_alert_date': (timezone.localdate() + timedelta(days=30)).isoformat(),
        }
        data.update(overrides)
        return MaintenanceForm(data=data)

    def test_rejects_future_maintenance_date(self):
        form = self.build_form(date=(timezone.localdate() + timedelta(days=1)).isoformat())

        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)

    def test_rejects_non_positive_maintenance_cost(self):
        form = self.build_form(cost='0')

        self.assertFalse(form.is_valid())
        self.assertIn('cost', form.errors)

    def test_rejects_next_alert_date_before_maintenance_date(self):
        form = self.build_form(next_alert_date=(timezone.localdate() - timedelta(days=1)).isoformat())

        self.assertFalse(form.is_valid())
        self.assertIn('next_alert_date', form.errors)

    def test_rejects_invalid_invoice_type(self):
        invoice = SimpleUploadedFile('invoice.exe', b'bad-file', content_type='application/octet-stream')
        form = MaintenanceForm(
            data={
                'vehicle': self.vehicle.pk,
                'type': 'P',
                'date': timezone.localdate().isoformat(),
                'description': 'Revisao preventiva',
                'cost': '450.00',
                'odometer': 8200,
                'workshop': 'Oficina Centro',
                'next_alert_km': 9000,
                'next_alert_date': (timezone.localdate() + timedelta(days=30)).isoformat(),
            },
            files={'invoice': invoice},
        )

        self.assertFalse(form.is_valid())
        self.assertIn('invoice', form.errors)

    def test_rejects_oversized_invoice(self):
        invoice = SimpleUploadedFile(
            'invoice.pdf',
            b'x' * (5 * 1024 * 1024 + 1),
            content_type='application/pdf',
        )
        form = MaintenanceForm(
            data={
                'vehicle': self.vehicle.pk,
                'type': 'P',
                'date': timezone.localdate().isoformat(),
                'description': 'Revisao preventiva',
                'cost': '450.00',
                'odometer': 8200,
                'workshop': 'Oficina Centro',
                'next_alert_km': 9000,
                'next_alert_date': (timezone.localdate() + timedelta(days=30)).isoformat(),
            },
            files={'invoice': invoice},
        )

        self.assertFalse(form.is_valid())
        self.assertIn('invoice', form.errors)
