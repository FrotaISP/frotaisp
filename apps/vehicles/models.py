# apps/vehicles/models.py
from django.db import models
from django.utils import timezone
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


class VehicleDocument(TimeStampedModel):
    DOCUMENT_TYPES = [
        ('crlv', 'CRLV'),
        ('licensing', 'Licenciamento'),
        ('insurance', 'Seguro'),
        ('antt', 'ANTT'),
        ('contract', 'Contrato'),
        ('inspection', 'Vistoria'),
        ('driver_license', 'CNH'),
        ('other', 'Outro'),
    ]

    company = models.ForeignKey('accounts.Company', on_delete=models.PROTECT, related_name='vehicle_documents', verbose_name='Empresa')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='documents', verbose_name='Veiculo', null=True, blank=True)
    driver = models.ForeignKey('drivers.Driver', on_delete=models.CASCADE, related_name='documents', verbose_name='Motorista', null=True, blank=True)
    document_type = models.CharField('Tipo', max_length=30, choices=DOCUMENT_TYPES)
    title = models.CharField('Titulo', max_length=120)
    number = models.CharField('Numero', max_length=80, blank=True)
    issue_date = models.DateField('Emissao', null=True, blank=True)
    expiration_date = models.DateField('Vencimento')
    file = models.FileField('Arquivo', upload_to='documents/', blank=True)
    notes = models.TextField('Observacoes', blank=True)
    is_active = models.BooleanField('Ativo', default=True)

    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['expiration_date', 'title']

    def __str__(self):
        target = self.vehicle or self.driver or self.company
        return f'{self.get_document_type_display()} - {target}'

    @property
    def days_until_expiration(self):
        return (self.expiration_date - timezone.localdate()).days

    @property
    def is_expired(self):
        return self.days_until_expiration < 0

    @property
    def is_expiring_soon(self):
        return 0 <= self.days_until_expiration <= 30


class VehicleChecklist(TimeStampedModel):
    STATUS_CHOICES = [
        ('approved', 'Aprovado'),
        ('attention', 'Requer atencao'),
        ('blocked', 'Bloqueado'),
    ]

    company = models.ForeignKey('accounts.Company', on_delete=models.PROTECT, related_name='vehicle_checklists', verbose_name='Empresa')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='checklists', verbose_name='Veiculo')
    driver = models.ForeignKey('drivers.Driver', on_delete=models.SET_NULL, related_name='checklists', verbose_name='Motorista', null=True, blank=True)
    inspected_at = models.DateTimeField('Data da inspecao', default=timezone.now)
    odometer = models.IntegerField('Hodometro', null=True, blank=True)
    tires_ok = models.BooleanField('Pneus em bom estado', default=True)
    oil_ok = models.BooleanField('Oleo/fluido ok', default=True)
    brakes_ok = models.BooleanField('Freios ok', default=True)
    lights_ok = models.BooleanField('Luzes e sinalizacao ok', default=True)
    safety_items_ok = models.BooleanField('Itens de seguranca ok', default=True)
    cleanliness_ok = models.BooleanField('Limpeza/conservacao ok', default=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='approved')
    notes = models.TextField('Observacoes', blank=True)
    photo = models.ImageField('Foto', upload_to='checklists/', blank=True, null=True)

    class Meta:
        verbose_name = 'Checklist de Veiculo'
        verbose_name_plural = 'Checklists de Veiculos'
        ordering = ['-inspected_at']

    def __str__(self):
        return f'{self.vehicle.plate} - {self.inspected_at:%d/%m/%Y %H:%M}'

    @property
    def has_issues(self):
        return not all([
            self.tires_ok,
            self.oil_ok,
            self.brakes_ok,
            self.lights_ok,
            self.safety_items_ok,
            self.cleanliness_ok,
        ]) or self.status in ('attention', 'blocked')

    def save(self, *args, **kwargs):
        if not self.company_id and self.vehicle_id:
            self.company = self.vehicle.company
        if self.odometer and self.odometer > self.vehicle.current_odometer:
            self.vehicle.current_odometer = self.odometer
            self.vehicle.save(update_fields=['current_odometer', 'updated_at'])
        super().save(*args, **kwargs)
