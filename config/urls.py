# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Autenticação
    path('accounts/', include(('apps.accounts.urls', 'accounts'), namespace='accounts')),

    # Dashboard (página inicial)
    path('', include(('apps.dashboard.urls', 'dashboard'), namespace='dashboard')),

    # Módulos do sistema
    path('veiculos/', include(('apps.vehicles.urls', 'vehicles'), namespace='vehicles')),
    path('motoristas/', include(('apps.drivers.urls', 'drivers'), namespace='drivers')),
    path('viagens/', include(('apps.trips.urls', 'trips'), namespace='trips')),
    path('combustivel/', include(('apps.fuel.urls', 'fuel'), namespace='fuel')),
    path('manutencoes/', include(('apps.maintenance.urls', 'maintenance'), namespace='maintenance')),
    path('relatorios/', include(('apps.reports.urls', 'reports'), namespace='reports')),

    # APIs REST (todas sob /api/)
    path('api/dashboard/', include('apps.dashboard.api.urls')),
    path('api/vehicles/', include('apps.vehicles.api.urls')),
    # Futuramente:
    # path('api/drivers/', include('apps.drivers.api.urls')),
    # path('api/trips/', include('apps.trips.api.urls')),
    # path('api/fuel/', include('apps.fuel.api.urls')),
]

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)