from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.drivers.models import Driver
from apps.trips.models import Trip
from apps.vehicles.models import Vehicle


class VehicleViewIntegrationTests(TestCase):
    def setUp(self):
        self.operator = self.create_user('vehicle-operator', 'operator')
        self.manager = self.create_user('vehicle-manager', 'manager')
        self.driver_user = self.create_user('vehicle-driver', 'driver')
        self.driver = Driver.objects.create(
            user=self.driver_user,
            cnh='44444444444',
            cnh_expiration='2030-01-01',
            phone='(62) 96666-5555',
        )

    def create_user(self, username, role):
        user = User.objects.create_user(username=username, password='senha123')
        UserProfile.objects.update_or_create(user=user, defaults={'role': role})
        return user

    def test_operator_can_create_vehicle_via_view(self):
        self.client.force_login(self.operator)

        response = self.client.post(reverse('vehicles:create'), data={
            'plate': 'XYZ1234',
            'brand': 'Fiat',
            'model': 'Strada',
            'year': 2024,
            'chassis': 'CHASSI123',
            'fuel_type': 'F',
            'capacity_kg': '650.00',
            'current_odometer': 1200,
            'is_active': 'on',
            'current_driver': self.driver.pk,
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Vehicle.objects.filter(plate='XYZ1234').exists())

    def test_manager_cannot_delete_vehicle_with_trip_history(self):
        vehicle = Vehicle.objects.create(
            plate='XYZ5678',
            brand='Toyota',
            model='Hilux',
            year=2023,
            fuel_type='D',
            current_odometer=10000,
        )
        Trip.objects.create(
            vehicle=vehicle,
            driver=self.driver,
            start_time=timezone.now(),
            end_time=timezone.now(),
            start_odometer=10000,
            end_odometer=10100,
            destination='Cliente',
            purpose='Visita tecnica',
            service_order='OS-200',
        )

        self.client.force_login(self.manager)
        response = self.client.post(reverse('vehicles:delete', args=[vehicle.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Vehicle.objects.filter(pk=vehicle.pk).exists())
