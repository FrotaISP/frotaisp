from django import forms

from .models import Trip


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = [
            'vehicle',
            'driver',
            'start_time',
            'end_time',
            'start_odometer',
            'end_odometer',
            'destination',
            'purpose',
            'service_order',
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'driver': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'start_odometer': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'end_odometer': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'purpose': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'service_order': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned = super().clean()
        vehicle = cleaned.get('vehicle')
        start_time = cleaned.get('start_time')
        end_time = cleaned.get('end_time')
        start_odometer = cleaned.get('start_odometer')
        end_odometer = cleaned.get('end_odometer')

        if start_time and end_time and end_time < start_time:
            self.add_error('end_time', 'O horário final não pode ser anterior ao horário inicial.')

        if start_odometer is not None and end_odometer is not None and end_odometer < start_odometer:
            self.add_error('end_odometer', 'O km final não pode ser menor que o km inicial.')

        if vehicle and start_time:
            conflicts = Trip.objects.filter(vehicle=vehicle).exclude(pk=self.instance.pk)

            if end_time:
                conflicts = conflicts.filter(start_time__lte=end_time).filter(
                    forms.models.Q(end_time__isnull=True) | forms.models.Q(end_time__gte=start_time)
                )
            else:
                conflicts = conflicts.filter(
                    forms.models.Q(end_time__isnull=True) |
                    forms.models.Q(end_time__gte=start_time)
                )

            if conflicts.exists():
                self.add_error('vehicle', 'Já existe uma viagem sobreposta para este veículo no período informado.')

        return cleaned
