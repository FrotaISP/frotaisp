# apps/vehicles/admin.py
from django.contrib import admin
from .models import Tire, TireEvent, Vehicle, VehicleChecklist, VehicleDocument


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate', 'model', 'brand', 'year', 'current_odometer', 'tracking_status', 'last_location_at', 'is_active', 'current_driver')
    list_filter = ('is_active', 'brand', 'fuel_type')
    search_fields = ('plate', 'model', 'brand')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Dados do veiculo', {
            'fields': ('company', 'plate', 'brand', 'model', 'year', 'chassis', 'fuel_type', 'capacity_kg', 'current_odometer', 'is_active', 'image', 'current_driver')
        }),
        ('Rastreamento', {
            'fields': ('latitude', 'longitude', 'last_location_at', 'last_speed_kmh', 'heading_degrees', 'location_source')
        }),
        ('Auditoria', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(VehicleDocument)
class VehicleDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'vehicle', 'driver', 'expiration_date', 'is_active')
    list_filter = ('document_type', 'expiration_date', 'is_active')
    search_fields = ('title', 'number', 'vehicle__plate', 'driver__user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VehicleChecklist)
class VehicleChecklistAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'driver', 'inspected_at', 'status', 'odometer')
    list_filter = ('status', 'inspected_at')
    search_fields = ('vehicle__plate', 'driver__user__username', 'notes')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Tire)
class TireAdmin(admin.ModelAdmin):
    list_display = ('code', 'brand', 'size', 'status', 'current_vehicle', 'position', 'current_tread_mm')
    list_filter = ('status', 'brand', 'current_vehicle')
    search_fields = ('code', 'brand', 'model', 'size', 'current_vehicle__plate')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(TireEvent)
class TireEventAdmin(admin.ModelAdmin):
    list_display = ('tire', 'event_type', 'vehicle', 'date', 'odometer', 'cost')
    list_filter = ('event_type', 'date')
    search_fields = ('tire__code', 'vehicle__plate', 'notes')
    readonly_fields = ('created_at', 'updated_at')
