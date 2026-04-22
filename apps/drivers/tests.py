from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.drivers.forms import DriverCreateForm, DriverUpdateForm
from apps.accounts.models import UserProfile
from apps.drivers.models import Driver
from apps.vehicles.models import Vehicle
from apps.trips.models import Trip


class DriverCreateFormTests(TestCase):
    def test_save_sets_user_profile_role_to_driver(self):
        form = DriverCreateForm(data={
            'first_name': 'Carlos',
            'last_name': 'Silva',
            'email': 'carlos@example.com',
            'username': 'carlos.silva',
            'password': 'senha123',
            'cnh': '12345678901',
            'cnh_expiration': '2030-01-01',
            'phone': '(62) 99999-9999',
            'address': 'Rua A, 10',
            'is_available': 'on',
        })

        self.assertTrue(form.is_valid(), form.errors)

        driver = form.save()

        profile = UserProfile.objects.get(user=driver.user)
        self.assertEqual(profile.role, 'driver')

    def test_rejects_invalid_avatar_upload_type(self):
        avatar = SimpleUploadedFile('avatar.pdf', b'fake-pdf', content_type='application/pdf')
        form = DriverCreateForm(
            data={
                'first_name': 'Carlos',
                'last_name': 'Silva',
                'email': 'carlos@example.com',
                'username': 'carlos.avatar',
                'password': 'senha123',
                'cnh': '12345678903',
                'cnh_expiration': '2030-01-01',
                'phone': '(62) 99999-9999',
                'address': 'Rua A, 10',
                'is_available': 'on',
            },
            files={'avatar': avatar},
        )

        self.assertFalse(form.is_valid())
        self.assertIn('avatar', form.errors)

    def test_update_keeps_user_profile_role_as_driver(self):
        create_form = DriverCreateForm(data={
            'first_name': 'Carlos',
            'last_name': 'Silva',
            'email': 'carlos@example.com',
            'username': 'carlos.update',
            'password': 'senha123',
            'cnh': '12345678902',
            'cnh_expiration': '2030-01-01',
            'phone': '(62) 99999-9999',
            'address': 'Rua A, 10',
            'is_available': 'on',
        })
        self.assertTrue(create_form.is_valid(), create_form.errors)
        driver = create_form.save()

        profile = UserProfile.objects.get(user=driver.user)
        profile.role = 'viewer'
        profile.save(update_fields=['role'])

        update_form = DriverUpdateForm(data={
            'first_name': 'Carlos',
            'last_name': 'Souza',
            'email': 'carlos@example.com',
            'cnh': driver.cnh,
            'cnh_expiration': '2031-01-01',
            'phone': '(62) 98888-7777',
            'address': 'Rua B, 20',
            'is_available': 'on',
        }, instance=driver)

        self.assertTrue(update_form.is_valid(), update_form.errors)
        update_form.save()

        profile.refresh_from_db()
        self.assertEqual(profile.role, 'driver')


class DriverViewIntegrationTests(TestCase):
    def setUp(self):
        self.operator = self.create_user('driver-operator', 'operator')
        self.manager = self.create_user('driver-manager', 'manager')
        self.driver_user = self.create_user('history-driver-user', 'driver')
        self.history_driver = Driver.objects.create(
            user=self.driver_user,
            cnh='55555555555',
            cnh_expiration='2030-01-01',
            phone='(62) 97777-1111',
        )
        self.vehicle = Vehicle.objects.create(
            plate='DRV1234',
            brand='Fiat',
            model='Toro',
            year=2024,
            fuel_type='F',
            current_odometer=2000,
        )

    def create_user(self, username, role):
        user = User.objects.create_user(username=username, password='senha123')
        UserProfile.objects.update_or_create(user=user, defaults={'role': role})
        return user

    def test_operator_can_create_driver_via_view(self):
        self.client.force_login(self.operator)

        response = self.client.post(reverse('drivers:create'), data={
            'first_name': 'Novo',
            'last_name': 'Motorista',
            'email': 'novo.motorista@example.com',
            'username': 'novo.motorista',
            'password': 'senha123',
            'cnh': '66666666666',
            'cnh_expiration': '2031-01-01',
            'phone': '(62) 98888-1234',
            'address': 'Rua Teste, 123',
            'is_available': 'on',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Driver.objects.filter(cnh='66666666666').exists())

    def test_manager_cannot_delete_driver_with_trip_history(self):
        Trip.objects.create(
            vehicle=self.vehicle,
            driver=self.history_driver,
            start_time=timezone.now(),
            end_time=timezone.now(),
            start_odometer=2000,
            end_odometer=2100,
            destination='Cliente',
            purpose='Atendimento',
            service_order='OS-300',
        )

        self.client.force_login(self.manager)
        response = self.client.post(reverse('drivers:delete', args=[self.history_driver.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Driver.objects.filter(pk=self.history_driver.pk).exists())
