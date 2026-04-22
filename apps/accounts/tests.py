from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import UserProfile


class RegisterViewTests(TestCase):
    def test_public_registration_forces_viewer_role(self):
        response = self.client.post(reverse('accounts:register'), data={
            'username': 'novo.usuario',
            'email': 'novo@example.com',
            'first_name': 'Novo',
            'last_name': 'Usuario',
            'password1': 'SenhaSegura123',
            'password2': 'SenhaSegura123',
            'role': 'admin',
            'phone': '(62) 99999-0000',
        })

        self.assertEqual(response.status_code, 302)

        profile = UserProfile.objects.get(user__username='novo.usuario')
        self.assertEqual(profile.role, 'viewer')
        self.assertEqual(profile.phone, '(62) 99999-0000')

    def test_public_registration_form_does_not_expose_role_field(self):
        response = self.client.get(reverse('accounts:register'))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('role', response.context['form'].fields)
