# apps/fuel/forms.py
from django import forms
from django.utils import timezone
from apps.core.mixins import scope_related_queryset_for_user
from apps.core.uploads import ALLOWED_DOCUMENT_TYPES, validate_uploaded_file
from .models import FuelRecord
from apps.vehicles.models import Vehicle


class FuelRecordForm(forms.ModelForm):
    class Meta:
        model = FuelRecord
        fields = [
            'vehicle', 'date', 'liters', 'price_per_liter', 'odometer', 'gas_station',
            'station_city', 'payment_method', 'is_full_tank', 'notes', 'photo', 'receipt',
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'liters': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'price_per_liter': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'odometer': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'gas_station': forms.TextInput(attrs={'class': 'form-control'}),
            'station_city': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'is_full_tank': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'receipt': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, company=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company or getattr(self.instance, 'company', None)
        self.user = user
        if user:
            self.fields['vehicle'].queryset = scope_related_queryset_for_user(Vehicle.objects.filter(is_active=True), user)

    def clean_vehicle(self):
        vehicle = self.cleaned_data.get('vehicle')
        if vehicle and self.company and vehicle.company_id and vehicle.company_id != self.company.id:
            raise forms.ValidationError('Selecione um veiculo da sua empresa.')
        return vehicle

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.localdate():
            raise forms.ValidationError('A data do abastecimento nao pode estar no futuro.')
        return date

    def clean_liters(self):
        liters = self.cleaned_data.get('liters')
        if liters is not None and liters <= 0:
            raise forms.ValidationError('A quantidade de litros deve ser maior que zero.')
        return liters

    def clean_price_per_liter(self):
        price_per_liter = self.cleaned_data.get('price_per_liter')
        if price_per_liter is not None and price_per_liter <= 0:
            raise forms.ValidationError('O preco por litro deve ser maior que zero.')
        return price_per_liter

    def clean_odometer(self):
        vehicle = self.cleaned_data.get('vehicle')
        odometer = self.cleaned_data.get('odometer')

        if vehicle and odometer is not None:
            current_km = vehicle.current_odometer

            if odometer < current_km:
                raise forms.ValidationError(
                    f'O hodometro informado ({odometer:,} km) e menor que o hodometro '
                    f'atual do veiculo {vehicle.plate} ({current_km:,} km). '
                    f'Verifique o valor e tente novamente.'
                )

            last_fuel = (
                FuelRecord.objects
                .filter(vehicle=vehicle)
                .exclude(pk=self.instance.pk if self.instance.pk else None)
                .order_by('-odometer')
                .values_list('odometer', flat=True)
                .first()
            )
            if last_fuel and odometer < last_fuel:
                raise forms.ValidationError(
                    f'O hodometro informado ({odometer:,} km) e menor que o do ultimo '
                    f'abastecimento registrado ({last_fuel:,} km).'
                )

        return odometer

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        try:
            validate_uploaded_file(photo, allowed_types=['image/jpeg', 'image/png', 'image/webp'], label='A foto do abastecimento')
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc
        return photo

    def clean_receipt(self):
        receipt = self.cleaned_data.get('receipt')
        try:
            validate_uploaded_file(receipt, allowed_types=ALLOWED_DOCUMENT_TYPES, label='O comprovante')
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc
        return receipt

    def save(self, commit=True):
        record = super().save(commit=False)
        if self.company and not record.company_id:
            record.company = self.company
        if commit:
            record.save()
            self.save_m2m()
        return record
