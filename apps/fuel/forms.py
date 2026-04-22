# apps/fuel/forms.py
from django import forms
from django.utils import timezone
from apps.core.uploads import ALLOWED_DOCUMENT_TYPES, validate_uploaded_file
from .models import FuelRecord
from apps.vehicles.models import Vehicle


class FuelRecordForm(forms.ModelForm):
    class Meta:
        model = FuelRecord
        fields = ['vehicle', 'date', 'liters', 'price_per_liter', 'odometer', 'gas_station', 'receipt']
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'liters': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'price_per_liter': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'odometer': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'gas_station': forms.TextInput(attrs={'class': 'form-control'}),
            'receipt': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.localdate():
            raise forms.ValidationError('A data do abastecimento não pode estar no futuro.')
        return date

    def clean_liters(self):
        liters = self.cleaned_data.get('liters')
        if liters is not None and liters <= 0:
            raise forms.ValidationError('A quantidade de litros deve ser maior que zero.')
        return liters

    def clean_price_per_liter(self):
        price_per_liter = self.cleaned_data.get('price_per_liter')
        if price_per_liter is not None and price_per_liter <= 0:
            raise forms.ValidationError('O preço por litro deve ser maior que zero.')
        return price_per_liter

    def clean_odometer(self):
        vehicle = self.cleaned_data.get('vehicle')
        odometer = self.cleaned_data.get('odometer')

        if vehicle and odometer is not None:
            current_km = vehicle.current_odometer

            if odometer < current_km:
                raise forms.ValidationError(
                    f'O hodômetro informado ({odometer:,} km) é menor que o hodômetro '
                    f'atual do veículo {vehicle.plate} ({current_km:,} km). '
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
                    f'O hodômetro informado ({odometer:,} km) é menor que o do último '
                    f'abastecimento registrado ({last_fuel:,} km).'
                )

        return odometer

    def clean_receipt(self):
        receipt = self.cleaned_data.get('receipt')
        try:
            validate_uploaded_file(
                receipt,
                allowed_types=ALLOWED_DOCUMENT_TYPES,
                label='O comprovante',
            )
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc
        return receipt
