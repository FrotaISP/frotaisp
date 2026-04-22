# apps/maintenance/forms.py
from django import forms
from .models import Maintenance
from apps.fuel.models import FuelRecord


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = [
            'vehicle', 'type', 'date', 'description', 'cost',
            'odometer', 'workshop', 'next_alert_km', 'next_alert_date', 'invoice'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'odometer': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'workshop': forms.TextInput(attrs={'class': 'form-control'}),
            'next_alert_km': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'next_alert_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'invoice': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

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

            # Verifica contra último abastecimento
            last_fuel = (
                FuelRecord.objects
                .filter(vehicle=vehicle)
                .order_by('-odometer')
                .values_list('odometer', flat=True)
                .first()
            )
            if last_fuel and odometer < last_fuel:
                raise forms.ValidationError(
                    f'O hodômetro ({odometer:,} km) é menor que o do último '
                    f'abastecimento registrado ({last_fuel:,} km).'
                )

        return odometer

    def clean(self):
        cleaned = super().clean()
        next_km = cleaned.get('next_alert_km')
        odometer = cleaned.get('odometer')

        if next_km and odometer and next_km <= odometer:
            raise forms.ValidationError(
                'O km do próximo alerta deve ser maior que o hodômetro atual da manutenção.'
            )
        return cleaned
