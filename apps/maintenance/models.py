# apps/maintenance/models.py
from django.db import models
from apps.core.models import TimeStampedModel

class Maintenance(TimeStampedModel):
    MAINTENANCE_TYPES = [
        ('P', 'Preventiva'),
        ('C', 'Corretiva'),
        ('E', 'Emergencial'),
    ]

    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.PROTECT,
        related_name='maintenances',
        verbose_name='Veículo'
    )
    type = models.CharField('Tipo', max_length=1, choices=MAINTENANCE_TYPES)
    date = models.DateField('Data')
    description = models.TextField('Descrição')
    cost = models.DecimalField('Custo', max_digits=8, decimal_places=2)
    odometer = models.IntegerField('Km no Momento')
    workshop = models.CharField('Oficina', max_length=100)
    next_alert_km = models.IntegerField('Alerta próx. manutenção (km)', null=True, blank=True)
    next_alert_date = models.DateField('Alerta próx. manutenção (data)', null=True, blank=True)
    invoice = models.FileField('Nota Fiscal', upload_to='maintenance_invoices/', blank=True)

    class Meta:
        verbose_name = 'Manutenção'
        verbose_name_plural = 'Manutenções'
        ordering = ['-date']

    def __str__(self):
        return f"{self.vehicle.plate} - {self.get_type_display()} - {self.date}"