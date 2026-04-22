# apps/drivers/admin.py
from django.contrib import admin
from .models import Driver

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'cnh', 'cnh_expiration', 'phone', 'is_available')
    list_filter = ('is_available',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'cnh')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Documentos', {
            'fields': ('cnh', 'cnh_expiration')
        }),
        ('Contato', {
            'fields': ('phone', 'address')
        }),
        ('Status', {
            'fields': ('is_available', 'avatar')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )