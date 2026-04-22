from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.dashboard.api.views import dashboard_summary
from apps.drivers.models import Driver
from apps.trips.models import Trip
from apps.vehicles.models import Vehicle


class DashboardApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='api-dashboard', password='senha123')
        UserProfile.objects.update_or_create(user=self.user, defaults={'role': 'manager'})
        self.driver = Driver.objects.create(
            user=self.user,
            cnh='99999999999',
            cnh_expiration='2030-01-01',
            phone='(62) 97777-2222',
            is_available=True,
        )
        self.vehicle = Vehicle.objects.create(
            plate='API1234',
            brand='Renault',
            model='Duster',
            year=2024,
            fuel_type='F',
            current_odometer=3000,
            is_active=True,
        )
        Trip.objects.create(
            vehicle=self.vehicle,
            driver=self.driver,
            start_time=timezone.now(),
            end_time=None,
            start_odometer=3000,
            end_odometer=None,
            destination='Cliente API',
            purpose='Instalacao',
            service_order='OS-API',
        )

    def test_dashboard_summary_requires_authentication(self):
        response = self.client.get('/api/dashboard/summary/')

        self.assertEqual(response.status_code, 403)

    def test_dashboard_summary_returns_expected_fields(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/dashboard/summary/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('total_vehicles', response.json())
        self.assertIn('available_drivers', response.json())
        self.assertIn('drivers_in_trip', response.json())
        self.assertEqual(response.json()['drivers_in_trip'], 1)
