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


class WorkOrder(TimeStampedModel):
    STATUS_CHOICES = [
        ('open', 'Aberta'),
        ('scheduled', 'Agendada'),
        ('in_progress', 'Em andamento'),
        ('waiting_parts', 'Aguardando pecas'),
        ('completed', 'Concluida'),
        ('cancelled', 'Cancelada'),
    ]
    PRIORITY_CHOICES = PreventiveMaintenancePlan.PRIORITY_CHOICES
    CATEGORY_CHOICES = [
        ('maintenance', 'Manutencao'),
        ('fuel', 'Abastecimento'),
        ('tires', 'Pneus'),
        ('damage', 'Avaria'),
        ('document', 'Documento'),
        ('other', 'Outro'),
    ]

    company = models.ForeignKey('accounts.Company', on_delete=models.PROTECT, related_name='work_orders', verbose_name='Empresa')
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.PROTECT, related_name='work_orders', verbose_name='Veiculo')
    driver = models.ForeignKey('drivers.Driver', on_delete=models.SET_NULL, related_name='work_orders', verbose_name='Motorista', null=True, blank=True)
    title = models.CharField('Titulo', max_length=140)
    category = models.CharField('Categoria', max_length=30, choices=CATEGORY_CHOICES, default='maintenance')
    priority = models.CharField('Prioridade', max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='open')
    opened_at = models.DateTimeField('Aberta em', default=timezone.now)
    scheduled_date = models.DateField('Data agendada', null=True, blank=True)
    completed_at = models.DateTimeField('Concluida em', null=True, blank=True)
    odometer = models.IntegerField('Hodometro', null=True, blank=True)
    description = models.TextField('Descricao')
    resolution = models.TextField('Resolucao', blank=True)
    estimated_cost = models.DecimalField('Custo estimado', max_digits=10, decimal_places=2, default=0)
    actual_cost = models.DecimalField('Custo realizado', max_digits=10, decimal_places=2, default=0)
    attachment = models.FileField('Anexo', upload_to='work_orders/', blank=True)

    class Meta:
        verbose_name = 'Ordem de Servico'
        verbose_name_plural = 'Ordens de Servico'
        ordering = ['status', '-opened_at']

    def __str__(self):
        return f'OS #{self.pk or "nova"} - {self.title}'

    def save(self, *args, **kwargs):
        if not self.company_id and self.vehicle_id:
            self.company = self.vehicle.company
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)


class VehicleExpense(TimeStampedModel):
    CATEGORY_CHOICES = [
        ('fuel', 'Combustivel'),
        ('maintenance', 'Manutencao'),
        ('tires', 'Pneus'),
        ('documents', 'Documentos'),
        ('insurance', 'Seguro'),
        ('taxes', 'Taxas e impostos'),
        ('other', 'Outros'),
    ]

    company = models.ForeignKey('accounts.Company', on_delete=models.PROTECT, related_name='vehicle_expenses', verbose_name='Empresa')
    vehicle = models.ForeignKey('vehicles.Vehicle', on_delete=models.PROTECT, related_name='expenses', verbose_name='Veiculo', null=True, blank=True)
    work_order = models.ForeignKey(WorkOrder, on_delete=models.SET_NULL, related_name='expenses', verbose_name='Ordem de servico', null=True, blank=True)
    date = models.DateField('Data', default=timezone.localdate)
    category = models.CharField('Categoria', max_length=30, choices=CATEGORY_CHOICES)
    cost_center = models.CharField('Centro de custo', max_length=100, blank=True)
    supplier = models.CharField('Fornecedor', max_length=120, blank=True)
    description = models.CharField('Descricao', max_length=180)
    amount = models.DecimalField('Valor', max_digits=10, decimal_places=2)
    receipt = models.FileField('Comprovante', upload_to='expenses/', blank=True)
    notes = models.TextField('Observacoes', blank=True)

    class Meta:
        verbose_name = 'Despesa de Frota'
        verbose_name_plural = 'Despesas de Frota'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.get_category_display()} - R$ {self.amount}'

    def save(self, *args, **kwargs):
        if not self.company_id:
            if self.vehicle_id:
                self.company = self.vehicle.company
            elif self.work_order_id:
                self.company = self.work_order.company
        super().save(*args, **kwargs)
