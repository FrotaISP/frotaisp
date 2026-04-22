# apps/fuel/forms.py
from django import forms
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

    def clean_odometer(self):
        vehicle = self.cleaned_data.get('vehicle')
        odometer = self.cleaned_data.get('odometer')

        if vehicle and odometer is not None:
            current_km = vehicle.current_odometer

            # O hodômetro do abastecimento não pode ser menor que o hodômetro atual do veículo
            if odometer < current_km:
                raise forms.ValidationError(
                    f'O hodômetro informado ({odometer:,} km) é menor que o hodômetro '
                    f'atual do veículo {vehicle.plate} ({current_km:,} km). '
                    f'Verifique o valor e tente novamente.'
                )

            # Também verifica contra o último abastecimento deste veículo
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
