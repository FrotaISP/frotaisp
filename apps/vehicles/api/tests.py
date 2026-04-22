from django.contrib.auth.models import User
from django.test import TestCase

from apps.accounts.models import UserProfile
from apps.vehicles.models import Vehicle


class VehicleApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='api-vehicle', password='senha123')
        UserProfile.objects.update_or_create(user=self.user, defaults={'role': 'manager'})
        Vehicle.objects.create(
            plate='CAR1111',
            brand='Fiat',
            model='Strada',
            year=2024,
            fuel_type='F',
            current_odometer=1000,
            is_active=True,
        )
        Vehicle.objects.create(
            plate='CAR2222',
            brand='Ford',
            model='Ranger',
            year=2023,
            fuel_type='D',
            current_odometer=2000,
            is_active=False,
        )

    def test_vehicle_list_requires_authentication(self):
        response = self.client.get('/api/vehicles/')

        self.assertEqual(response.status_code, 403)

    def test_vehicle_list_returns_only_active_vehicles(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/vehicles/')

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['count'], 1)
        self.assertEqual(payload['results'][0]['plate'], 'CAR1111')
