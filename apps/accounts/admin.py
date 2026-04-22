# apps/accounts/admin.py
from django.contrib import admin

from .models import Company, Notificacao, UserProfile


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan', 'subscription_status', 'trial_ends_at', 'max_users', 'max_vehicles', 'is_active')
    list_filter = ('plan', 'subscription_status', 'is_active')
    search_fields = ('name', 'slug', 'billing_email', 'billing_document')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Empresa', {'fields': ('name', 'slug', 'is_active')}),
        ('Assinatura', {'fields': ('plan', 'subscription_status', 'trial_ends_at', 'subscription_started_at', 'subscription_ends_at')}),
        ('Limites', {'fields': ('max_users', 'max_vehicles')}),
        ('Financeiro', {'fields': ('billing_email', 'billing_document')}),
        ('Auditoria', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'role', 'phone')
    list_filter = ('role', 'company')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'company__name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'lida', 'criada_em')
    list_filter = ('tipo', 'lida', 'criada_em')
    search_fields = ('usuario__username', 'mensagem')
    readonly_fields = ('criada_em',)
