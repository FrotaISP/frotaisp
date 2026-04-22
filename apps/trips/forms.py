from django import forms
from django.db.models import Q

from apps.core.mixins import scope_related_queryset_for_user
from apps.drivers.models import Driver
from apps.vehicles.models import Vehicle
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

    def __init__(self, *args, company=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company or getattr(self.instance, 'company', None)
        self.user = user
        if user:
            self.fields['vehicle'].queryset = scope_related_queryset_for_user(Vehicle.objects.filter(is_active=True), user)
            self.fields['driver'].queryset = scope_related_queryset_for_user(Driver.objects.select_related('user'), user)

    def clean(self):
        cleaned = super().clean()
        vehicle = cleaned.get('vehicle')
        driver = cleaned.get('driver')
        start_time = cleaned.get('start_time')
        end_time = cleaned.get('end_time')
        start_odometer = cleaned.get('start_odometer')
        end_odometer = cleaned.get('end_odometer')

        if vehicle and self.company and vehicle.company_id and vehicle.company_id != self.company.id:
            self.add_error('vehicle', 'Selecione um veiculo da sua empresa.')
        if driver and self.company and driver.company_id and driver.company_id != self.company.id:
            self.add_error('driver', 'Selecione um motorista da sua empresa.')

        if start_time and end_time and end_time < start_time:
            self.add_error('end_time', 'O horario final nao pode ser anterior ao horario inicial.')

        if start_odometer is not None and end_odometer is not None and end_odometer < start_odometer:
            self.add_error('end_odometer', 'O km final nao pode ser menor que o km inicial.')

        if vehicle and start_time:
            conflicts = Trip.objects.filter(vehicle=vehicle).exclude(pk=self.instance.pk)

            if end_time:
                conflicts = conflicts.filter(start_time__lte=end_time).filter(
                    Q(end_time__isnull=True) | Q(end_time__gte=start_time)
                )
            else:
                conflicts = conflicts.filter(
                    Q(end_time__isnull=True) |
                    Q(end_time__gte=start_time)
                )

            if conflicts.exists():
                self.add_error('vehicle', 'Ja existe uma viagem sobreposta para este veiculo no periodo informado.')

        return cleaned

    def save(self, commit=True):
        trip = super().save(commit=False)
        if self.company and not trip.company_id:
            trip.company = self.company
        if commit:
            trip.save()
            self.save_m2m()
        return trip
