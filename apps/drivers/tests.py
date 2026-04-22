from django.test import TestCase

from apps.drivers.forms import DriverCreateForm
from apps.accounts.models import UserProfile


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
