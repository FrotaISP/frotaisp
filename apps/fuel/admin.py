# apps/fuel/admin.py
from django.contrib import admin
from .models import FuelRecord

@admin.register(FuelRecord)
class FuelRecordAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'date', 'liters', 'price_per_liter', 'total_cost', 'odometer', 'gas_station')
    list_filter = ('vehicle', 'date', 'gas_station')
    search_fields = ('vehicle__plate', 'gas_station')
    readonly_fields = ('total_cost', 'created_at', 'updated_at')
    fieldsets = (
        ('Informações do Abastecimento', {
            'fields': ('vehicle', 'date', 'odometer', 'gas_station')
        }),
        ('Quantidade e Valores', {
            'fields': ('liters', 'price_per_liter', 'total_cost')
        }),
        ('Comprovante', {
            'fields': ('receipt',)
        }),
        ('Datas do Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )