# apps/accounts/middleware.py
from django.contrib import messages
from django.contrib.auth import logout
from django.db import DatabaseError, OperationalError, ProgrammingError
from django.shortcuts import redirect
from django.urls import reverse

from apps.core.mixins import get_user_company, get_user_profile


class CompanySubscriptionMiddleware:
    """Bloqueia uso operacional quando a empresa esta sem acesso ativo."""

    ALLOWED_PREFIXES = (
        '/accounts/assinatura/',
        '/accounts/logout/',
        '/accounts/login/',
        '/accounts/registro/',
        '/admin/',
        '/static/',
        '/media/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._should_block(request):
            profile = get_user_profile(request.user)
            messages.error(request, 'Sua assinatura precisa de atencao para continuar usando o sistema.')
            if profile.is_manager:
                return redirect(reverse('accounts:subscription'))
            logout(request)
            messages.error(request, 'Apenas gestores e administradores podem regularizar a assinatura.')
            return redirect(reverse('accounts:login'))
        return self.get_response(request)

    def _should_block(self, request):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated or user.is_superuser:
            return False
        if request.path.startswith(self.ALLOWED_PREFIXES):
            return False
        try:
            company = get_user_company(user)
        except (DatabaseError, OperationalError, ProgrammingError):
            return False
        return bool(company and not company.has_active_access)
