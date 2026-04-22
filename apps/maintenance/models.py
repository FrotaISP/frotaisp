# apps/maintenance/models.py
from datetime import timedelta
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel


class Maintenance(TimeStampedModel):
    MAINTENANCE_TYPES = [
        ('P', 'Preventiva'),
        ('C', 'Corretiva'),
        ('E', 'Emergencial'),
    ]

    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.PROTECT,
        related_name='maintenances',
        verbose_name='Empresa',
        null=True,
        blank=True,
    )
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.PROTECT,
        related_name='maintenances',
        verbose_name='Veiculo'
    )
    type = models.CharField('Tipo', max_length=1, choices=MAINTENANCE_TYPES)
    date = models.DateField('Data')
    description = models.TextField('Descricao')
    cost = models.DecimalField('Custo', max_digits=8, decimal_places=2)
    odometer = models.IntegerField('Km no Momento')
    workshop = models.CharField('Oficina', max_length=100)
    next_alert_km = models.IntegerField('Alerta prox. manutencao (km)', null=True, blank=True)
    next_alert_date = models.DateField('Alerta prox. manutencao (data)', null=True, blank=True)
    invoice = models.FileField('Nota Fiscal', upload_to='maintenance_invoices/', blank=True)

    class Meta:
        verbose_name = 'Manutencao'
        verbose_name_plural = 'Manutencoes'
        ordering = ['-date']

    def __str__(self):
        return f"{self.vehicle.plate} - {self.get_type_display()} - {self.date}"

    def save(self, *args, **kwargs):
        if not self.company_id and self.vehicle_id:
            self.company = self.vehicle.company
        super().save(*args, **kwargs)

        if self.odometer > self.vehicle.current_odometer:
            self.vehicle.current_odometer = self.odometer
            self.vehicle.save(update_fields=['current_odometer', 'updated_at'])


class PreventiveMaintenancePlan(TimeStampedModel):
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('paused', 'Pausado'),
        ('completed', 'Concluido'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Baixa'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Critica'),
    ]

    company = models.ForeignKey('accounts.Company', on_delete=models.PROTECT, related_name='maintenance_plans', verbose_name='Empresa')
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.PROTECT, related_name='maintenance_plans', verbose_name='Veiculo')
    service_name = models.CharField('Servico preventivo', max_length=120)
    description = models.TextField('Descricao', blank=True)
    frequency_km = models.IntegerField('Recorrencia por km', null=True, blank=True)
    frequency_days = models.IntegerField('Recorrencia por dias', null=True, blank=True)
    last_service_date = models.DateField('Ultima execucao', null=True, blank=True)
    last_service_km = models.IntegerField('Km da ultima execucao', null=True, blank=True)
    next_due_date = models.DateField('Proxima data', null=True, blank=True)
    next_due_km = models.IntegerField('Proximo km', null=True, blank=True)
    priority = models.CharField('Prioridade', max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField('Observacoes', blank=True)

    class Meta:
        verbose_name = 'Plano de Manutencao Preventiva'
        verbose_name_plural = 'Planos de Manutencao Preventiva'
        ordering = ['status', 'next_due_date', 'next_due_km']

    def __str__(self):
        return f'{self.vehicle.plate} - {self.service_name}'

    def save(self, *args, **kwargs):
        if not self.company_id and self.vehicle_id:
            self.company = self.vehicle.company
        if self.frequency_days and self.last_service_date and not self.next_due_date:
            self.next_due_date = self.last_service_date + timedelta(days=self.frequency_days)
        if self.frequency_km and self.last_service_km and not self.next_due_km:
            self.next_due_km = self.last_service_km + self.frequency_km
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        today = timezone.localdate()
        due_by_date = self.next_due_date and self.next_due_date < today
        due_by_km = self.next_due_km and self.vehicle.current_odometer >= self.next_due_km
        return self.status == 'active' and bool(due_by_date or due_by_km)

    @property
    def is_due_soon(self):
        today = timezone.localdate()
        due_by_date = self.next_due_date and today <= self.next_due_date <= today + timedelta(days=15)
        due_by_km = self.next_due_km and self.vehicle.current_odometer >= self.next_due_km - 500
        return self.status == 'active' and bool(due_by_date or due_by_km)
