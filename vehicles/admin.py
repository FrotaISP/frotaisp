# apps/vehicles/admin.py
from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate', 'model', 'brand', 'year', 'current_odometer', 'is_active', 'current_driver')
    list_filter = ('is_active', 'brand', 'fuel_type')
    search_fields = ('plate', 'model', 'brand')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('plate', 'brand', 'model', 'year', 'chassis', 'fuel_type')
        }),
        ('Medidas e Status', {
            'fields': ('capacity_kg', 'current_odometer', 'is_active', 'current_driver')
        }),
        ('Imagem', {
            'fields': ('image',)
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )