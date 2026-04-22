# apps/maintenance/forms.py
from django import forms
from django.utils import timezone
from apps.core.mixins import scope_related_queryset_for_user
from apps.core.uploads import ALLOWED_DOCUMENT_TYPES, validate_uploaded_file
from .models import Maintenance, PreventiveMaintenancePlan
from apps.fuel.models import FuelRecord
from apps.vehicles.models import Vehicle


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
            raise forms.ValidationError('A data da manutencao nao pode estar no futuro.')
        return date

    def clean_cost(self):
        cost = self.cleaned_data.get('cost')
        if cost is not None and cost <= 0:
            raise forms.ValidationError('O custo da manutencao deve ser maior que zero.')
        return cost

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
                .order_by('-odometer')
                .values_list('odometer', flat=True)
                .first()
            )
            if last_fuel and odometer < last_fuel:
                raise forms.ValidationError(
                    f'O hodometro ({odometer:,} km) e menor que o do ultimo '
                    f'abastecimento registrado ({last_fuel:,} km).'
                )

        return odometer

    def clean_invoice(self):
        invoice = self.cleaned_data.get('invoice')
        try:
            validate_uploaded_file(invoice, allowed_types=ALLOWED_DOCUMENT_TYPES, label='O comprovante da manutencao')
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
            raise forms.ValidationError('O km do proximo alerta deve ser maior que o hodometro atual da manutencao.')

        if date and next_alert_date and next_alert_date <= date:
            self.add_error('next_alert_date', 'A data do proximo alerta deve ser posterior a data da manutencao.')

        return cleaned

    def save(self, commit=True):
        record = super().save(commit=False)
        if self.company and not record.company_id:
            record.company = self.company
        if commit:
            record.save()
            self.save_m2m()
        return record


class PreventiveMaintenancePlanForm(forms.ModelForm):
    class Meta:
        model = PreventiveMaintenancePlan
        fields = [
            'vehicle', 'service_name', 'description', 'frequency_km', 'frequency_days',
            'last_service_date', 'last_service_km', 'next_due_date', 'next_due_km',
            'priority', 'status', 'notes'
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'service_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Troca de oleo'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'frequency_km': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'frequency_days': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'last_service_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'last_service_km': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'next_due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'next_due_km': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, company=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company or getattr(self.instance, 'company', None)
        if user:
            self.fields['vehicle'].queryset = scope_related_queryset_for_user(Vehicle.objects.filter(is_active=True), user)

    def clean_vehicle(self):
        vehicle = self.cleaned_data.get('vehicle')
        if vehicle and self.company and vehicle.company_id != self.company.id:
            raise forms.ValidationError('Selecione um veiculo da sua empresa.')
        return vehicle

    def clean(self):
        cleaned = super().clean()
        frequency_km = cleaned.get('frequency_km')
        frequency_days = cleaned.get('frequency_days')
        next_due_km = cleaned.get('next_due_km')
        last_service_km = cleaned.get('last_service_km')
        next_due_date = cleaned.get('next_due_date')
        last_service_date = cleaned.get('last_service_date')

        if not frequency_km and not frequency_days and not next_due_km and not next_due_date:
            raise forms.ValidationError('Informe uma recorrencia ou uma proxima data/km para o plano preventivo.')
        if last_service_km and next_due_km and next_due_km <= last_service_km:
            self.add_error('next_due_km', 'O proximo km deve ser maior que o km da ultima execucao.')
        if last_service_date and next_due_date and next_due_date <= last_service_date:
            self.add_error('next_due_date', 'A proxima data deve ser posterior a ultima execucao.')
        return cleaned

    def save(self, commit=True):
        plan = super().save(commit=False)
        if self.company and not plan.company_id:
            plan.company = self.company
        if commit:
            plan.save()
            self.save_m2m()
        return plan
