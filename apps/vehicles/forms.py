# apps/vehicles/forms.py
from django import forms
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

    def clean_current_odometer(self):
        new_km = self.cleaned_data.get('current_odometer')
        # Na edição, valida que o novo valor não é menor que o atual salvo
        if self.instance and self.instance.pk:
            current = Vehicle.objects.values_list('current_odometer', flat=True).get(pk=self.instance.pk)
            if new_km is not None and new_km < current:
                raise forms.ValidationError(
                    f'O hodômetro não pode ser reduzido. '
                    f'Valor atual registrado: {current:,} km. '
                    f'Valor informado: {new_km:,} km.'
                )
        return new_km
