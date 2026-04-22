# apps/vehicles/forms.py
from django import forms
from django.utils import timezone
from apps.core.mixins import scope_related_queryset_for_user
from apps.core.uploads import ALLOWED_DOCUMENT_TYPES, ALLOWED_IMAGE_TYPES, validate_uploaded_file
from apps.drivers.models import Driver
from .models import Tire, TireEvent, Vehicle, VehicleChecklist, VehicleDocument


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['plate', 'brand', 'model', 'year', 'chassis', 'fuel_type', 'capacity_kg', 'current_odometer', 'is_active', 'image', 'current_driver']
        widgets = {
            'plate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: ABC-1234'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'chassis': forms.TextInput(attrs={'class': 'form-control'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select'}),
            'capacity_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'current_odometer': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'current_driver': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, company=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company or getattr(self.instance, 'company', None)
        self.user = user
        if user:
            self.fields['current_driver'].queryset = scope_related_queryset_for_user(Driver.objects.select_related('user'), user)

    def clean_plate(self):
        plate = self.cleaned_data['plate'].upper().strip()
        qs = Vehicle.objects.filter(plate=plate).exclude(pk=self.instance.pk)
        if self.company:
            qs = qs.filter(company=self.company)
        if qs.exists():
            raise forms.ValidationError('Esta placa ja esta cadastrada para esta empresa.')
        return plate

    def clean_current_driver(self):
        driver = self.cleaned_data.get('current_driver')
        if driver and self.company and driver.company_id and driver.company_id != self.company.id:
            raise forms.ValidationError('Selecione um motorista da mesma empresa do veiculo.')
        return driver

    def clean_current_odometer(self):
        new_km = self.cleaned_data.get('current_odometer')
        if self.instance and self.instance.pk:
            current = Vehicle.objects.values_list('current_odometer', flat=True).get(pk=self.instance.pk)
            if new_km is not None and new_km < current:
                raise forms.ValidationError(f'O hodometro nao pode ser reduzido. Valor atual registrado: {current:,} km. Valor informado: {new_km:,} km.')
        return new_km

    def save(self, commit=True):
        vehicle = super().save(commit=False)
        if self.company and not vehicle.company_id:
            vehicle.company = self.company
        if commit:
            vehicle.save()
            self.save_m2m()
        return vehicle


class VehicleDocumentForm(forms.ModelForm):
    class Meta:
        model = VehicleDocument
        fields = ['vehicle', 'driver', 'document_type', 'title', 'number', 'issue_date', 'expiration_date', 'file', 'notes', 'is_active']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, company=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company or getattr(self.instance, 'company', None)
        if user:
            self.fields['vehicle'].queryset = scope_related_queryset_for_user(Vehicle.objects.all(), user)
            self.fields['driver'].queryset = scope_related_queryset_for_user(Driver.objects.select_related('user'), user)

    def clean(self):
        cleaned = super().clean()
        vehicle = cleaned.get('vehicle')
        driver = cleaned.get('driver')
        issue_date = cleaned.get('issue_date')
        expiration_date = cleaned.get('expiration_date')
        if not vehicle and not driver:
            raise forms.ValidationError('Informe um veiculo ou motorista para vincular o documento.')
        if vehicle and self.company and vehicle.company_id != self.company.id:
            self.add_error('vehicle', 'Selecione um veiculo da sua empresa.')
        if driver and self.company and driver.company_id != self.company.id:
            self.add_error('driver', 'Selecione um motorista da sua empresa.')
        if issue_date and expiration_date and expiration_date < issue_date:
            self.add_error('expiration_date', 'O vencimento nao pode ser anterior a emissao.')
        return cleaned

    def clean_file(self):
        file = self.cleaned_data.get('file')
        try:
            validate_uploaded_file(file, allowed_types=ALLOWED_DOCUMENT_TYPES, label='O documento')
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc
        return file

    def save(self, commit=True):
        document = super().save(commit=False)
        if self.company and not document.company_id:
            document.company = self.company
        if commit:
            document.save()
            self.save_m2m()
        return document


class VehicleChecklistForm(forms.ModelForm):
    class Meta:
        model = VehicleChecklist
        fields = ['vehicle', 'driver', 'inspected_at', 'odometer', 'tires_ok', 'oil_ok', 'brakes_ok', 'lights_ok', 'safety_items_ok', 'cleanliness_ok', 'status', 'notes', 'photo']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'inspected_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'odometer': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, company=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company or getattr(self.instance, 'company', None)
        if user:
            self.fields['vehicle'].queryset = scope_related_queryset_for_user(Vehicle.objects.filter(is_active=True), user)
            self.fields['driver'].queryset = scope_related_queryset_for_user(Driver.objects.select_related('user'), user)

    def clean_vehicle(self):
        vehicle = self.cleaned_data.get('vehicle')
        if vehicle and self.company and vehicle.company_id != self.company.id:
            raise forms.ValidationError('Selecione um veiculo da sua empresa.')
        return vehicle

    def clean_driver(self):
        driver = self.cleaned_data.get('driver')
        if driver and self.company and driver.company_id != self.company.id:
            raise forms.ValidationError('Selecione um motorista da sua empresa.')
        return driver

    def clean_inspected_at(self):
        inspected_at = self.cleaned_data.get('inspected_at')
        if inspected_at and inspected_at > timezone.now():
            raise forms.ValidationError('A inspecao nao pode estar no futuro.')
        return inspected_at

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        try:
            validate_uploaded_file(photo, allowed_types=ALLOWED_IMAGE_TYPES, label='A foto do checklist')
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc
        return photo

    def save(self, commit=True):
        checklist = super().save(commit=False)
        if self.company and not checklist.company_id:
            checklist.company = self.company
        if commit:
            checklist.save()
            self.save_m2m()
        return checklist


class TireForm(forms.ModelForm):
    class Meta:
        model = Tire
        fields = ['code', 'brand', 'model', 'size', 'purchase_date', 'purchase_cost', 'initial_tread_mm', 'current_tread_mm', 'current_vehicle', 'position', 'installed_odometer', 'status', 'notes']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'size': forms.TextInput(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'purchase_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'initial_tread_mm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'current_tread_mm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'current_vehicle': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'installed_odometer': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, company=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company or getattr(self.instance, 'company', None)
        if user:
            self.fields['current_vehicle'].queryset = scope_related_queryset_for_user(Vehicle.objects.filter(is_active=True), user)

    def clean_code(self):
        code = self.cleaned_data['code'].strip().upper()
        qs = Tire.objects.filter(code=code).exclude(pk=self.instance.pk)
        if self.company:
            qs = qs.filter(company=self.company)
        if qs.exists():
            raise forms.ValidationError('Este codigo de pneu ja esta cadastrado para esta empresa.')
        return code

    def save(self, commit=True):
        tire = super().save(commit=False)
        if self.company and not tire.company_id:
            tire.company = self.company
        if commit:
            tire.save()
            self.save_m2m()
        return tire


class TireEventForm(forms.ModelForm):
    class Meta:
        model = TireEvent
        fields = ['tire', 'vehicle', 'event_type', 'date', 'odometer', 'position', 'tread_mm', 'cost', 'notes']
        widgets = {
            'tire': forms.Select(attrs={'class': 'form-select'}),
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'odometer': forms.NumberInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'tread_mm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, company=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company or getattr(self.instance, 'company', None)
        if user:
            self.fields['tire'].queryset = scope_related_queryset_for_user(Tire.objects.all(), user)
            self.fields['vehicle'].queryset = scope_related_queryset_for_user(Vehicle.objects.filter(is_active=True), user)

    def clean(self):
        cleaned = super().clean()
        tire = cleaned.get('tire')
        vehicle = cleaned.get('vehicle')
        event_type = cleaned.get('event_type')
        if tire and self.company and tire.company_id != self.company.id:
            self.add_error('tire', 'Selecione um pneu da sua empresa.')
        if vehicle and self.company and vehicle.company_id != self.company.id:
            self.add_error('vehicle', 'Selecione um veiculo da sua empresa.')
        if event_type in ('install', 'rotation') and not vehicle:
            self.add_error('vehicle', 'Informe o veiculo para instalacao ou rodizio.')
        return cleaned

    def save(self, commit=True):
        event = super().save(commit=False)
        if self.company and not event.company_id:
            event.company = self.company
        if commit:
            event.save()
            self.save_m2m()
        return event
