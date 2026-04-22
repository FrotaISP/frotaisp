# apps/vehicles/models.py
from django.db import models
from apps.core.models import TimeStampedModel


class Vehicle(TimeStampedModel):
    FUEL_CHOICES = [
        ('G', 'Gasolina'),
        ('E', 'Etanol'),
        ('D', 'Diesel'),
        ('F', 'Flex'),
        ('H', 'Hibrido'),
        ('EL', 'Eletrico'),
    ]

    company = models.ForeignKey(
        'accounts.Company',
        on_delete=models.PROTECT,
        related_name='vehicles',
        verbose_name='Empresa',
        null=True,
        blank=True,
    )
    plate = models.CharField('Placa', max_length=8)
    brand = models.CharField('Marca', max_length=50)
    model = models.CharField('Modelo', max_length=50)
    year = models.IntegerField('Ano')
    chassis = models.CharField('Chassi', max_length=30, blank=True)
    fuel_type = models.CharField('Combustivel', max_length=2, choices=FUEL_CHOICES)
    capacity_kg = models.DecimalField('Capacidade (kg)', max_digits=6, decimal_places=2, null=True, blank=True)
    current_odometer = models.IntegerField('Hodometro Atual (km)', default=0)
    is_active = models.BooleanField('Ativo', default=True)
    image = models.ImageField('Foto', upload_to='vehicles/', blank=True, null=True)
    current_driver = models.ForeignKey(
        'drivers.Driver',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_vehicles',
        verbose_name='Motorista Atual'
    )

    class Meta:
        verbose_name = 'Veiculo'
        verbose_name_plural = 'Veiculos'
        ordering = ['plate']
        constraints = [
            models.UniqueConstraint(fields=['company', 'plate'], name='unique_vehicle_plate_per_company'),
        ]

    def save(self, *args, **kwargs):
        if not self.company_id:
            from apps.accounts.models import Company
            self.company = Company.get_default_company()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.plate} - {self.model}"
