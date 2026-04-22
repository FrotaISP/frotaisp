# apps/maintenance/models.py
from django.db import models
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
