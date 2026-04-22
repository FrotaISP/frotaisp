# apps/accounts/models.py
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Company(models.Model):
    PLAN_CHOICES = [
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    SUBSCRIPTION_STATUS_CHOICES = [
        ('trial', 'Periodo de teste'),
        ('active', 'Ativa'),
        ('past_due', 'Pagamento pendente'),
        ('suspended', 'Suspensa'),
        ('cancelled', 'Cancelada'),
    ]
    PLAN_LIMITS = {
        'starter': {'users': 3, 'vehicles': 10},
        'professional': {'users': 10, 'vehicles': 50},
        'enterprise': {'users': 0, 'vehicles': 0},
    }

    name = models.CharField('Nome da empresa', max_length=150, unique=True)
    slug = models.SlugField('Identificador', max_length=160, unique=True)
    is_active = models.BooleanField('Ativa', default=True)
    plan = models.CharField('Plano', max_length=30, choices=PLAN_CHOICES, default='starter')
    subscription_status = models.CharField('Status da assinatura', max_length=30, choices=SUBSCRIPTION_STATUS_CHOICES, default='trial')
    billing_email = models.EmailField('E-mail financeiro', blank=True)
    billing_document = models.CharField('CPF/CNPJ', max_length=30, blank=True)
    trial_ends_at = models.DateField('Fim do teste', null=True, blank=True)
    subscription_started_at = models.DateField('Inicio da assinatura', null=True, blank=True)
    subscription_ends_at = models.DateField('Fim da assinatura', null=True, blank=True)
    max_users = models.PositiveIntegerField('Limite de usuarios', default=3, help_text='Use 0 para ilimitado.')
    max_vehicles = models.PositiveIntegerField('Limite de veiculos', default=10, help_text='Use 0 para ilimitado.')
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['name']

    def __str__(self):
        return self.name

    @classmethod
    def get_default_company(cls):
        company, _ = cls.objects.get_or_create(
            slug='empresa-principal',
            defaults={
                'name': 'Empresa Principal',
                'subscription_status': 'active',
                'plan': 'enterprise',
                'max_users': 0,
                'max_vehicles': 0,
            },
        )
        return company

    @classmethod
    def trial_end_date(cls):
        return timezone.localdate() + timedelta(days=14)

    def save(self, *args, **kwargs):
        if not self.trial_ends_at and self.subscription_status == 'trial':
            self.trial_ends_at = self.trial_end_date()
        if self.plan and (not self.max_users or not self.max_vehicles):
            limits = self.PLAN_LIMITS.get(self.plan, {})
            if not self.max_users:
                self.max_users = limits.get('users', 3)
            if not self.max_vehicles:
                self.max_vehicles = limits.get('vehicles', 10)
        super().save(*args, **kwargs)

    @property
    def is_trial(self):
        return self.subscription_status == 'trial'

    @property
    def is_trial_expired(self):
        return self.is_trial and self.trial_ends_at and self.trial_ends_at < timezone.localdate()

    @property
    def is_subscription_expired(self):
        return self.subscription_ends_at and self.subscription_ends_at < timezone.localdate()

    @property
    def has_active_access(self):
        if not self.is_active:
            return False
        if self.subscription_status in ('active', 'past_due'):
            return not self.is_subscription_expired
        if self.subscription_status == 'trial':
            return not self.is_trial_expired
        return False

    @property
    def days_until_trial_end(self):
        if not self.trial_ends_at:
            return None
        return (self.trial_ends_at - timezone.localdate()).days

    def users_count(self):
        return self.users.filter(user__is_active=True).count()

    def vehicles_count(self):
        return self.vehicles.filter(is_active=True).count()

    def can_add_user(self):
        return self.max_users == 0 or self.users_count() < self.max_users

    def can_add_vehicle(self):
        return self.max_vehicles == 0 or self.vehicles_count() < self.max_vehicles

    def usage_percent(self, used, limit):
        if not limit:
            return 0
        return min(int((used / limit) * 100), 100)


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
        related_name='profile', verbose_name='Usuario'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name='users',
        verbose_name='Empresa',
        null=True,
        blank=True,
    )
    role       = models.CharField('Papel',     max_length=20, choices=ROLE_CHOICES, default='viewer')
    phone      = models.CharField('Telefone',  max_length=20, blank=True)
    created_at = models.DateTimeField('Criado em',      auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em',  auto_now=True)

    class Meta:
        verbose_name        = 'Perfil de Usuario'
        verbose_name_plural = 'Perfis de Usuarios'

    def save(self, *args, **kwargs):
        if not self.company_id:
            self.company = Company.get_default_company()
        super().save(*args, **kwargs)

    def __str__(self):
        company = f' - {self.company.name}' if self.company_id else ''
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()}){company}"

    # -- Helpers de permissao ---------------------------------------------
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


# -- Notificacoes ----------------------------------------------------------
class Notificacao(models.Model):
    TIPOS = [
        ('info',    'Informacao'),
        ('alerta',  'Alerta'),
        ('sucesso', 'Sucesso'),
        ('erro',    'Erro'),
    ]

    usuario   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    mensagem  = models.TextField('Mensagem')
    tipo      = models.CharField('Tipo', max_length=10, choices=TIPOS, default='info')
    lida      = models.BooleanField('Lida', default=False)
    criada_em = models.DateTimeField('Criada em', auto_now_add=True)

    class Meta:
        verbose_name        = 'Notificacao'
        verbose_name_plural = 'Notificacoes'
        ordering            = ['-criada_em']

    def __str__(self):
        return f'{self.usuario.username} - {self.mensagem[:50]}'
