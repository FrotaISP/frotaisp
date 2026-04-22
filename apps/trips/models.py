# apps/trips/models.py
from django.db import models
from apps.core.models import TimeStampedModel
from apps.vehicles.models import Vehicle
from apps.drivers.models import Driver


class Trip(TimeStampedModel):
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.PROTECT,
        related_name='trips',
        verbose_name='Empresa',
        null=True,
        blank=True,
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name='trips',
        verbose_name='Veiculo'
    )
    driver = models.ForeignKey(
        Driver,
        on_delete=models.PROTECT,
        related_name='trips',
        verbose_name='Motorista'
    )
    start_time = models.DateTimeField('Inicio')
    end_time = models.DateTimeField('Fim', null=True, blank=True)
    start_odometer = models.IntegerField('Km Inicial')
    end_odometer = models.IntegerField('Km Final', null=True, blank=True)
    destination = models.CharField('Destino', max_length=255)
    purpose = models.TextField('Proposito')
    service_order = models.CharField('No OS', max_length=50, blank=True)

    class Meta:
        verbose_name = 'Viagem'
        verbose_name_plural = 'Viagens'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.vehicle.plate} - {self.start_time.strftime('%d/%m/%Y %H:%M')}"

    def distance(self):
        if self.end_odometer:
            return self.end_odometer - self.start_odometer
        return 0

    def save(self, *args, **kwargs):
        if not self.company_id and self.vehicle_id:
            self.company = self.vehicle.company
        super().save(*args, **kwargs)

        latest_odometer = self.end_odometer or self.start_odometer
        if latest_odometer > self.vehicle.current_odometer:
            self.vehicle.current_odometer = latest_odometer
            self.vehicle.save(update_fields=['current_odometer', 'updated_at'])
