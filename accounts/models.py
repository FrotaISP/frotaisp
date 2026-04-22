# apps/accounts/models.py
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin',    'Administrador'),
        ('manager',  'Gestor'),
        ('operator', 'Operador'),
        ('driver',   'Motorista'),
        ('viewer',   'Visualizador'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='profile', verbose_name='Usuário'
    )
    role = models.CharField('Papel', max_length=20, choices=ROLE_CHOICES, default='viewer')
    phone = models.CharField('Telefone', max_length=20, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_superuser

    @property
    def is_manager(self):
        return self.role in ('admin', 'manager') or self.user.is_superuser

    @property
    def is_operator(self):
        return self.role in ('admin', 'manager', 'operator') or self.user.is_superuser

    @property
    def is_driver(self):
        return self.role == 'driver'

    def can_edit(self):
        return self.is_operator

    def can_delete(self):
        return self.is_manager

    def can_manage_users(self):
        return self.is_admin

    def can_register_fuel(self):
        return self.role in ('admin', 'manager', 'operator', 'driver') or self.user.is_superuser

    def can_register_trip(self):
        return self.role in ('admin', 'manager', 'operator', 'driver') or self.user.is_superuser

    def can_register_maintenance(self):
        return self.is_operator
