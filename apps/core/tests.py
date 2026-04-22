from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import UserProfile
from apps.drivers.models import Driver
from apps.vehicles.models import Vehicle


class PermissionMixinViewTests(TestCase):
    def setUp(self):
        self.viewer = self.create_user('viewer-user', 'viewer')
        self.driver_user = self.create_user('driver-user', 'driver')
        self.operator = self.create_user('operator-user', 'operator')
        self.manager = self.create_user('manager-user', 'manager')

        self.driver_profile = Driver.objects.create(
            user=self.driver_user,
            cnh='33333333333',
            cnh_expiration='2030-01-01',
            phone='(62) 97777-8888',
        )
        self.vehicle = Vehicle.objects.create(
            plate='MNO7890',
            brand='Toyota',
            model='Hilux',
            year=2023,
            fuel_type='D',
            current_odometer=15000,
        )

    def create_user(self, username, role):
        user = User.objects.create_user(username=username, password='senha123')
        UserProfile.objects.update_or_create(user=user, defaults={'role': role})
        return user

    def test_viewer_cannot_access_vehicle_create(self):
        self.client.force_login(self.viewer)

        response = self.client.get(reverse('vehicles:create'))

        self.assertEqual(response.status_code, 302)

    def test_driver_can_access_trip_and_fuel_create_views(self):
        self.client.force_login(self.driver_user)

        trip_response = self.client.get(reverse('trips:create'))
        fuel_response = self.client.get(reverse('fuel:create'))

        self.assertEqual(trip_response.status_code, 200)
        self.assertEqual(fuel_response.status_code, 200)

    def test_driver_cannot_access_maintenance_create_view(self):
        self.client.force_login(self.driver_user)

        response = self.client.get(reverse('maintenance:create'))

        self.assertEqual(response.status_code, 302)

    def test_operator_can_access_vehicle_and_maintenance_create_views(self):
        self.client.force_login(self.operator)

        vehicle_response = self.client.get(reverse('vehicles:create'))
        maintenance_response = self.client.get(reverse('maintenance:create'))

        self.assertEqual(vehicle_response.status_code, 200)
        self.assertEqual(maintenance_response.status_code, 200)

    def test_only_manager_can_access_vehicle_delete_view(self):
        self.client.force_login(self.operator)
        operator_response = self.client.get(reverse('vehicles:delete', args=[self.vehicle.pk]))

        self.client.force_login(self.manager)
        manager_response = self.client.get(reverse('vehicles:delete', args=[self.vehicle.pk]))

        self.assertEqual(operator_response.status_code, 302)
        self.assertEqual(manager_response.status_code, 200)
