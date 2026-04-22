# apps/core/admin.py
from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'company', 'action', 'method', 'status_code', 'path')
    list_filter = ('action', 'method', 'status_code', 'created_at')
    search_fields = ('user__username', 'path', 'object_repr', 'user_agent')
    readonly_fields = ('company', 'user', 'action', 'path', 'method', 'status_code', 'object_repr', 'ip_address', 'user_agent', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
