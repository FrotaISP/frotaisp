from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.drivers.forms import DriverCreateForm, DriverUpdateForm
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
