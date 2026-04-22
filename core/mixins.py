# apps/core/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect


def get_user_profile(user):
    """Retorna o perfil do usuário, criando um padrão se não existir."""
    from apps.accounts.models import UserProfile
    try:
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'admin' if user.is_superuser else 'viewer'}
        )
        return profile
    except Exception:
        # Tabela ainda não criada (antes da migration) — retorna objeto seguro
        class _FallbackProfile:
            role = 'admin' if user.is_superuser else 'viewer'
            is_admin = user.is_superuser
            is_manager = user.is_superuser
            is_operator = user.is_superuser
            is_driver = False
            def can_edit(self): return user.is_superuser
            def can_delete(self): return user.is_superuser
            def can_manage_users(self): return user.is_superuser
            def can_register_fuel(self): return user.is_superuser
            def can_register_trip(self): return user.is_superuser
            def can_register_maintenance(self): return user.is_superuser
        return _FallbackProfile()


def _deny(request, msg='Você não tem permissão para realizar esta ação.'):
    messages.error(request, msg)
    return redirect(request.META.get('HTTP_REFERER', '/'))


# ── Mixins reutilizáveis ──────────────────────────────────────────────────────

class OperatorRequiredMixin(LoginRequiredMixin):
    """Operador, Gestor ou Admin podem criar/editar registros gerais."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not get_user_profile(request.user).can_edit():
            return _deny(request)
        return super().dispatch(request, *args, **kwargs)


class ManagerRequiredMixin(LoginRequiredMixin):
    """Apenas Gestor ou Admin podem excluir."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not get_user_profile(request.user).can_delete():
            return _deny(request, 'Apenas gestores podem excluir registros.')
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin):
    """Apenas Admin pode gerenciar usuários."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not get_user_profile(request.user).can_manage_users():
            return _deny(request, 'Apenas administradores podem gerenciar usuários.')
        return super().dispatch(request, *args, **kwargs)


class FuelRegisterMixin(LoginRequiredMixin):
    """Motorista, Operador, Gestor e Admin podem registrar abastecimentos."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not get_user_profile(request.user).can_register_fuel():
            return _deny(request, 'Você não tem permissão para registrar abastecimentos.')
        return super().dispatch(request, *args, **kwargs)


class TripRegisterMixin(LoginRequiredMixin):
    """Motorista, Operador, Gestor e Admin podem registrar viagens."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not get_user_profile(request.user).can_register_trip():
            return _deny(request, 'Você não tem permissão para registrar viagens.')
        return super().dispatch(request, *args, **kwargs)


class MaintenanceRegisterMixin(LoginRequiredMixin):
    """Apenas Operador e acima podem registrar manutenções."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not get_user_profile(request.user).can_register_maintenance():
            return _deny(request, 'Você não tem permissão para registrar manutenções.')
        return super().dispatch(request, *args, **kwargs)
