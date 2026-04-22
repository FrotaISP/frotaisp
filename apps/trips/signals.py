# apps/trips/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Trip

@receiver(post_save, sender=Trip)
def update_vehicle_on_trip(sender, instance, created, **kwargs):
    """
    Ao criar/atualizar uma viagem:
    - Se a viagem foi finalizada (end_odometer preenchido), atualiza o hodômetro do veículo e libera o motorista.
    - Se a viagem foi iniciada (sem end_time), atribui o motorista ao veículo.
    """
    vehicle = instance.vehicle

    if instance.end_odometer:
        # Finalizada
        vehicle.current_odometer = instance.end_odometer
        vehicle.current_driver = None
        vehicle.save()
    elif not instance.end_time:
        # Em andamento (iniciada)
        vehicle.current_driver = instance.driver
        vehicle.save()