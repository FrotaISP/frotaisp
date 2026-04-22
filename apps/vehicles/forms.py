# apps/vehicles/forms.py
from django import forms
from apps.core.mixins import scope_related_queryset_for_user
from apps.drivers.models import Driver
from .models import Vehicle


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'plate', 'brand', 'model', 'year', 'chassis',
            'fuel_type', 'capacity_kg', 'current_odometer',
            'is_active', 'image', 'current_driver'
        ]
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
            self.fields['current_driver'].queryset = scope_related_queryset_for_user(
                Driver.objects.select_related('user'), user
            )

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
                raise forms.ValidationError(
                    f'O hodometro nao pode ser reduzido. '
                    f'Valor atual registrado: {current:,} km. '
                    f'Valor informado: {new_km:,} km.'
                )
        return new_km

    def save(self, commit=True):
        vehicle = super().save(commit=False)
        if self.company and not vehicle.company_id:
            vehicle.company = self.company
        if commit:
            vehicle.save()
            self.save_m2m()
        return vehicle
