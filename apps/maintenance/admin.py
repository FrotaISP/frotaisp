# apps/maintenance/admin.py
from django.contrib import admin
from .models import Maintenance

@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'type', 'date', 'odometer', 'cost', 'workshop', 'has_next_alert')
    list_filter = ('type', 'date', 'vehicle')
    search_fields = ('vehicle__plate', 'description', 'workshop')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('vehicle', 'type', 'date', 'odometer', 'workshop')
        }),
        ('Detalhes', {
            'fields': ('description', 'cost', 'invoice')
        }),
        ('Alertas Futuros', {
            'fields': ('next_alert_km', 'next_alert_date'),
            'description': 'Defina quando a próxima manutenção deve ser alertada (km ou data)'
        }),
        ('Datas do Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_next_alert(self, obj):
        return bool(obj.next_alert_km or obj.next_alert_date)
    has_next_alert.boolean = True
    has_next_alert.short_description = 'Possui alerta?'