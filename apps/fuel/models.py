# apps/fuel/models.py
from django.db import models
from apps.core.models import TimeStampedModel


class FuelRecord(TimeStampedModel):
    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.PROTECT,
        related_name='fuel_records',
        verbose_name='Empresa',
        null=True,
        blank=True,
    )
    vehicle = models.ForeignKey(
        'vehicles.Vehicle',
        on_delete=models.PROTECT,
        related_name='fuel_records',
        verbose_name='Veiculo'
    )
    date = models.DateField('Data')
    liters = models.DecimalField('Litros', max_digits=8, decimal_places=2)
    price_per_liter = models.DecimalField('Preco por Litro', max_digits=6, decimal_places=2)
    total_cost = models.DecimalField('Custo Total', max_digits=8, decimal_places=2, editable=False)
    odometer = models.IntegerField('Km no Abastecimento')
    gas_station = models.CharField('Posto', max_length=100)
    receipt = models.FileField('Nota Fiscal', upload_to='fuel_receipts/', blank=True)

    class Meta:
        verbose_name = 'Abastecimento'
        verbose_name_plural = 'Abastecimentos'
        ordering = ['-date', '-created_at']

    def save(self, *args, **kwargs):
        if not self.company_id and self.vehicle_id:
            self.company = self.vehicle.company
        self.total_cost = self.liters * self.price_per_liter
        super().save(*args, **kwargs)

        if self.odometer > self.vehicle.current_odometer:
            self.vehicle.current_odometer = self.odometer
            self.vehicle.save(update_fields=['current_odometer', 'updated_at'])

    def __str__(self):
        return f"{self.vehicle.plate} - {self.date} - {self.liters} L"
