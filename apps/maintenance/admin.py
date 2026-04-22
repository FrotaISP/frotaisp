# apps/maintenance/admin.py
from django.contrib import admin
from .models import Maintenance, PreventiveMaintenancePlan


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'type', 'date', 'odometer', 'cost', 'workshop', 'has_next_alert')
    list_filter = ('type', 'date', 'vehicle')
    search_fields = ('vehicle__plate', 'description', 'workshop')
    readonly_fields = ('created_at', 'updated_at')

    def has_next_alert(self, obj):
        return bool(obj.next_alert_km or obj.next_alert_date)
    has_next_alert.boolean = True
    has_next_alert.short_description = 'Possui alerta?'


@admin.register(PreventiveMaintenancePlan)
class PreventiveMaintenancePlanAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'vehicle', 'next_due_date', 'next_due_km', 'priority', 'status')
    list_filter = ('status', 'priority', 'next_due_date')
    search_fields = ('service_name', 'vehicle__plate', 'description')
    readonly_fields = ('created_at', 'updated_at')
