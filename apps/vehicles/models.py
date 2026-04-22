# apps/vehicles/models.py
from django.db import models
from apps.core.models import TimeStampedModel

class Vehicle(TimeStampedModel):
    FUEL_CHOICES = [
        ('G', 'Gasolina'),
        ('E', 'Etanol'),
        ('D', 'Diesel'),
        ('F', 'Flex'),
        ('H', 'Híbrido'),
        ('EL', 'Elétrico'),   # corrigido para evitar conflito
    ]

    plate = models.CharField('Placa', max_length=8, unique=True)
    brand = models.CharField('Marca', max_length=50)
    model = models.CharField('Modelo', max_length=50)
    year = models.IntegerField('Ano')
    chassis = models.CharField('Chassi', max_length=30, blank=True)
    fuel_type = models.CharField('Combustível', max_length=2, choices=FUEL_CHOICES)
    capacity_kg = models.DecimalField('Capacidade (kg)', max_digits=6, decimal_places=2, null=True, blank=True)
    current_odometer = models.IntegerField('Hodômetro Atual (km)', default=0)
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
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'
        ordering = ['plate']

    def __str__(self):
        return f"{self.plate} - {self.model}"