# apps/trips/admin.py
from django.contrib import admin
from .models import Trip

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'driver', 'start_time', 'end_time', 'destination', 'distance_display')
    list_filter = ('vehicle', 'driver', 'start_time')
    search_fields = ('destination', 'purpose', 'service_order', 'vehicle__plate', 'driver__user__username')
    readonly_fields = ('created_at', 'updated_at', 'distance_display')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('vehicle', 'driver', 'destination', 'purpose', 'service_order')
        }),
        ('Período e Quilometragem', {
            'fields': ('start_time', 'end_time', 'start_odometer', 'end_odometer')
        }),
        ('Datas do Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def distance_display(self, obj):
        return f"{obj.distance()} km"
    distance_display.short_description = 'Distância'