# apps/maintenance/forms.py
from django import forms
from django.utils import timezone
from apps.core.uploads import ALLOWED_DOCUMENT_TYPES, validate_uploaded_file
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

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > timezone.localdate():
            raise forms.ValidationError('A data da manutenção não pode estar no futuro.')
        return date

    def clean_cost(self):
        cost = self.cleaned_data.get('cost')
        if cost is not None and cost <= 0:
            raise forms.ValidationError('O custo da manutenção deve ser maior que zero.')
        return cost

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

    def clean_invoice(self):
        invoice = self.cleaned_data.get('invoice')
        try:
            validate_uploaded_file(
                invoice,
                allowed_types=ALLOWED_DOCUMENT_TYPES,
                label='O comprovante da manutenção',
            )
        except ValueError as exc:
            raise forms.ValidationError(str(exc)) from exc
        return invoice

    def clean(self):
        cleaned = super().clean()
        date = cleaned.get('date')
        next_km = cleaned.get('next_alert_km')
        odometer = cleaned.get('odometer')
        next_alert_date = cleaned.get('next_alert_date')

        if next_km and odometer and next_km <= odometer:
            raise forms.ValidationError(
                'O km do próximo alerta deve ser maior que o hodômetro atual da manutenção.'
            )

        if date and next_alert_date and next_alert_date <= date:
            self.add_error('next_alert_date', 'A data do próximo alerta deve ser posterior à data da manutenção.')

        return cleaned
