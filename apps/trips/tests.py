from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.drivers.models import Driver
from apps.trips.forms import TripForm
from apps.trips.models import Trip
from apps.vehicles.models import Vehicle


class TripModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='trip-driver', password='senha123')
        self.driver = Driver.objects.create(
            user=self.user,
            cnh='11111111111',
            cnh_expiration='2030-01-01',
            phone='(62) 99999-9999',
        )
        self.vehicle = Vehicle.objects.create(
            plate='ABC1234',
            brand='Fiat',
            model='Strada',
            year=2024,
            fuel_type='F',
            current_odometer=1000,
        )

    def test_save_updates_vehicle_current_odometer(self):
        Trip.objects.create(
            vehicle=self.vehicle,
            driver=self.driver,
            start_time=timezone.now(),
            end_time=timezone.now(),
            start_odometer=1100,
            end_odometer=1250,
            destination='Central',
            purpose='Atendimento tecnico',
            service_order='OS-1',
        )

        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.current_odometer, 1250)


class TripFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='trip-form-driver', password='senha123')
        self.driver = Driver.objects.create(
            user=self.user,
            cnh='22222222222',
            cnh_expiration='2030-01-01',
            phone='(62) 98888-9999',
        )
        self.vehicle = Vehicle.objects.create(
            plate='JKL3456',
            brand='Renault',
            model='Oroch',
            year=2023,
            fuel_type='F',
            current_odometer=5000,
        )
        self.start = timezone.now().replace(second=0, microsecond=0)

    def build_form(self, **overrides):
        data = {
            'vehicle': self.vehicle.pk,
            'driver': self.driver.pk,
            'start_time': self.start.strftime('%Y-%m-%dT%H:%M'),
            'end_time': (self.start + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
            'start_odometer': 5000,
            'end_odometer': 5100,
            'destination': 'Base',
            'purpose': 'Atendimento',
            'service_order': 'OS-10',
        }
        data.update(overrides)
        return TripForm(data=data)

    def test_rejects_end_time_before_start_time(self):
        form = self.build_form(end_time=(self.start - timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M'))

        self.assertFalse(form.is_valid())
        self.assertIn('end_time', form.errors)

    def test_rejects_end_odometer_smaller_than_start_odometer(self):
        form = self.build_form(end_odometer=4900)

        self.assertFalse(form.is_valid())
        self.assertIn('end_odometer', form.errors)

    def test_rejects_overlapping_trip_for_same_vehicle(self):
        Trip.objects.create(
            vehicle=self.vehicle,
            driver=self.driver,
            start_time=self.start,
            end_time=self.start + timedelta(hours=2),
            start_odometer=5000,
            end_odometer=5200,
            destination='Cliente A',
            purpose='Instalacao',
            service_order='OS-11',
        )

        form = self.build_form(
            start_time=(self.start + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M'),
            end_time=(self.start + timedelta(hours=1, minutes=30)).strftime('%Y-%m-%dT%H:%M'),
        )

        self.assertFalse(form.is_valid())
        self.assertIn('vehicle', form.errors)

    def test_rejects_trip_when_vehicle_has_open_trip(self):
        Trip.objects.create(
            vehicle=self.vehicle,
            driver=self.driver,
            start_time=self.start,
            end_time=None,
            start_odometer=5000,
            end_odometer=None,
            destination='Cliente B',
            purpose='Suporte',
            service_order='OS-12',
        )

        form = self.build_form(
            start_time=(self.start + timedelta(hours=3)).strftime('%Y-%m-%dT%H:%M'),
            end_time=(self.start + timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M'),
        )

        self.assertFalse(form.is_valid())
        self.assertIn('vehicle', form.errors)
