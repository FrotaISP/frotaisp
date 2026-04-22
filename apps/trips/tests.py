from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.drivers.models import Driver
from apps.trips.models import Trip
from apps.vehicles.models import Vehicle


class TripModelTests(TestCase):
    def test_save_updates_vehicle_current_odometer(self):
        user = User.objects.create_user(username='trip-driver', password='senha123')
        driver = Driver.objects.create(
            user=user,
            cnh='11111111111',
            cnh_expiration='2030-01-01',
            phone='(62) 99999-9999',
        )
        vehicle = Vehicle.objects.create(
            plate='ABC1234',
            brand='Fiat',
            model='Strada',
            year=2024,
            fuel_type='F',
            current_odometer=1000,
        )

        Trip.objects.create(
            vehicle=vehicle,
            driver=driver,
            start_time=timezone.now(),
            end_time=timezone.now(),
            start_odometer=1100,
            end_odometer=1250,
            destination='Central',
            purpose='Atendimento tecnico',
            service_order='OS-1',
        )

        vehicle.refresh_from_db()
        self.assertEqual(vehicle.current_odometer, 1250)
