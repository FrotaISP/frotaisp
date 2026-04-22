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
    latitude = models.DecimalField('Latitude', max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField('Longitude', max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_at = models.DateTimeField('Ultima posicao', null=True, blank=True)
    last_speed_kmh = models.DecimalField('Velocidade atual (km/h)', max_digits=6, decimal_places=2, null=True, blank=True)
    heading_degrees = models.PositiveSmallIntegerField('Direcao (graus)', null=True, blank=True)
    location_source = models.CharField('Origem do rastreamento', max_length=80, blank=True)

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

    @property
    def has_location(self):
        return self.latitude is not None and self.longitude is not None

    @property
    def tracking_status(self):
        if not self.has_location:
            return 'no_signal'
        if not self.last_location_at:
            return 'unknown'
        age_minutes = (timezone.now() - self.last_location_at).total_seconds() / 60
        if age_minutes <= 5:
            return 'online'
        if age_minutes <= 30:
            return 'delayed'
        return 'offline'


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


class Tire(TimeStampedModel):
    STATUS_CHOICES = [
        ('stock', 'Em estoque'),
        ('installed', 'Instalado'),
        ('repair', 'Em reparo'),
        ('retread', 'Recapagem'),
        ('retired', 'Descartado'),
    ]

    company = models.ForeignKey('accounts.Company', on_delete=models.PROTECT, related_name='tires', verbose_name='Empresa')
    code = models.CharField('Codigo', max_length=60)
    brand = models.CharField('Marca', max_length=80)
    model = models.CharField('Modelo', max_length=80, blank=True)
    size = models.CharField('Medida', max_length=40, blank=True)
    purchase_date = models.DateField('Data de compra', null=True, blank=True)
    purchase_cost = models.DecimalField('Custo de compra', max_digits=10, decimal_places=2, default=0)
    initial_tread_mm = models.DecimalField('Sulco inicial (mm)', max_digits=5, decimal_places=2, null=True, blank=True)
    current_tread_mm = models.DecimalField('Sulco atual (mm)', max_digits=5, decimal_places=2, null=True, blank=True)
    current_vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, related_name='tires', verbose_name='Veiculo atual', null=True, blank=True)
    position = models.CharField('Posicao', max_length=40, blank=True)
    installed_odometer = models.IntegerField('Km de instalacao', null=True, blank=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='stock')
    notes = models.TextField('Observacoes', blank=True)

    class Meta:
        verbose_name = 'Pneu'
        verbose_name_plural = 'Pneus'
        ordering = ['code']
        constraints = [
            models.UniqueConstraint(fields=['company', 'code'], name='unique_tire_code_per_company'),
        ]

    def __str__(self):
        return f'{self.code} - {self.brand}'

    @property
    def km_used(self):
        if self.current_vehicle_id and self.installed_odometer is not None:
            return max(self.current_vehicle.current_odometer - self.installed_odometer, 0)
        return 0


class TireEvent(TimeStampedModel):
    EVENT_TYPES = [
        ('install', 'Instalacao'),
        ('rotation', 'Rodizio'),
        ('removal', 'Remocao'),
        ('repair', 'Reparo'),
        ('retread', 'Recapagem'),
        ('retire', 'Descarte'),
    ]

    company = models.ForeignKey('accounts.Company', on_delete=models.PROTECT, related_name='tire_events', verbose_name='Empresa')
    tire = models.ForeignKey(Tire, on_delete=models.CASCADE, related_name='events', verbose_name='Pneu')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='tire_events', verbose_name='Veiculo', null=True, blank=True)
    event_type = models.CharField('Tipo', max_length=20, choices=EVENT_TYPES)
    date = models.DateField('Data', default=timezone.localdate)
    odometer = models.IntegerField('Hodometro', null=True, blank=True)
    position = models.CharField('Posicao', max_length=40, blank=True)
    tread_mm = models.DecimalField('Sulco medido (mm)', max_digits=5, decimal_places=2, null=True, blank=True)
    cost = models.DecimalField('Custo', max_digits=10, decimal_places=2, default=0)
    notes = models.TextField('Observacoes', blank=True)

    class Meta:
        verbose_name = 'Evento de Pneu'
        verbose_name_plural = 'Eventos de Pneus'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.tire.code} - {self.get_event_type_display()} - {self.date:%d/%m/%Y}'

    def save(self, *args, **kwargs):
        if not self.company_id and self.tire_id:
            self.company = self.tire.company
        super().save(*args, **kwargs)
        tire = self.tire
        if self.tread_mm is not None:
            tire.current_tread_mm = self.tread_mm
        if self.event_type in ('install', 'rotation'):
            tire.current_vehicle = self.vehicle
            tire.position = self.position
            tire.status = 'installed'
            if self.odometer is not None:
                tire.installed_odometer = self.odometer
        elif self.event_type == 'removal':
            tire.current_vehicle = None
            tire.position = ''
            tire.status = 'stock'
        elif self.event_type == 'repair':
            tire.status = 'repair'
        elif self.event_type == 'retread':
            tire.status = 'retread'
        elif self.event_type == 'retire':
            tire.current_vehicle = None
            tire.position = ''
            tire.status = 'retired'
        tire.save(update_fields=['current_tread_mm', 'current_vehicle', 'position', 'status', 'installed_odometer', 'updated_at'])
