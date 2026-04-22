# apps/trips/apps.py
from django.apps import AppConfig

class TripsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.trips'
    verbose_name = 'Viagens'

    def ready(self):
        import apps.trips.signals  # noqa