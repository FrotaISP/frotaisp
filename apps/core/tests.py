from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Company, UserProfile
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


class CompanyIsolationTests(TestCase):
    def setUp(self):
        self.company_a = Company.objects.create(name='Empresa A', slug='empresa-a')
        self.company_b = Company.objects.create(name='Empresa B', slug='empresa-b')
        self.user_a = self.create_user('manager-a', 'manager', self.company_a)
        self.user_b = self.create_user('manager-b', 'manager', self.company_b)
        self.driver_a = self.create_driver('driver-a', '11111111111', self.company_a)
        self.driver_b = self.create_driver('driver-b', '22222222222', self.company_b)
        self.vehicle_a = Vehicle.objects.create(
            company=self.company_a,
            plate='AAA1234',
            brand='Fiat',
            model='Toro',
            year=2024,
            fuel_type='F',
            current_odometer=1000,
        )
        self.vehicle_b = Vehicle.objects.create(
            company=self.company_b,
            plate='AAA1234',
            brand='Fiat',
            model='Strada',
            year=2024,
            fuel_type='F',
            current_odometer=1000,
        )

    def create_user(self, username, role, company):
        user = User.objects.create_user(username=username, password='senha123')
        UserProfile.objects.update_or_create(user=user, defaults={'role': role, 'company': company})
        return user

    def create_driver(self, username, cnh, company):
        user = self.create_user(username, 'driver', company)
        return Driver.objects.create(
            company=company,
            user=user,
            cnh=cnh,
            cnh_expiration='2030-01-01',
            phone='(62) 90000-0000',
        )

    def test_vehicle_list_only_shows_current_company(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse('vehicles:list'))
        self.assertContains(response, self.vehicle_a.plate)
        self.assertNotContains(response, self.vehicle_b.model)

    def test_vehicle_detail_blocks_other_company(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse('vehicles:detail', args=[self.vehicle_b.pk]))
        self.assertEqual(response.status_code, 404)

    def test_same_plate_and_cnh_can_exist_in_different_companies(self):
        duplicate_driver = Driver.objects.create(
            company=self.company_b,
            user=User.objects.create_user(username='driver-b-2', password='senha123'),
            cnh=self.driver_a.cnh,
            cnh_expiration='2030-01-01',
            phone='(62) 90000-0000',
        )
        UserProfile.objects.update_or_create(
            user=duplicate_driver.user,
            defaults={'role': 'driver', 'company': self.company_b},
        )
        self.assertEqual(Vehicle.objects.filter(plate='AAA1234').count(), 2)
        self.assertEqual(Driver.objects.filter(cnh=self.driver_a.cnh).count(), 2)

    def test_driver_options_are_limited_to_current_company(self):
        self.client.force_login(self.user_a)
        response = self.client.get(reverse('vehicles:create'))
        form = response.context['form']
        self.assertIn(self.driver_a, form.fields['current_driver'].queryset)
        self.assertNotIn(self.driver_b, form.fields['current_driver'].queryset)
