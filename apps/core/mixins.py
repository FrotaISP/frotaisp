# apps/core/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import ProtectedError, Q
from django.shortcuts import redirect


def get_user_profile(user):
    """Retorna o perfil do usuario, criando um padrao se nao existir."""
    from apps.accounts.models import Company, UserProfile
    try:
        profile, _ = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': 'admin' if user.is_superuser else 'viewer',
                'company': Company.get_default_company(),
            },
        )
        if not profile.company_id:
            profile.company = Company.get_default_company()
            profile.save(update_fields=['company', 'updated_at'])
        return profile
    except Exception:
        # Tabela ainda nao criada (antes da migration) - retorna objeto seguro.
        class _FallbackProfile:
            role = 'admin' if user.is_superuser else 'viewer'
            company = None
            company_id = None
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


def get_user_company(user):
    """Retorna a empresa ativa do usuario autenticado."""
    if not getattr(user, 'is_authenticated', False):
        return None
    return get_user_profile(user).company


def scope_queryset_for_user(queryset, user, company_field='company'):
    """Aplica isolamento por empresa, mantendo superusuarios com visao global."""
    if getattr(user, 'is_superuser', False):
        return queryset

    company = get_user_company(user)
    if not company:
        return queryset.none()

    return queryset.filter(**{company_field: company})


def scope_related_queryset_for_user(queryset, user, company_field='company'):
    """Filtra opcoes de formularios por empresa e preserva registros legados sem empresa."""
    if getattr(user, 'is_superuser', False):
        return queryset

    company = get_user_company(user)
    if not company:
        return queryset.none()

    return queryset.filter(Q(**{company_field: company}) | Q(**{f'{company_field}__isnull': True}))


def _deny(request, msg='Voce nao tem permissao para realizar esta acao.'):
    messages.error(request, msg)
    return redirect(request.META.get('HTTP_REFERER', '/'))


class ProtectedDeleteMixin:
    protected_error_message = 'Este registro nao pode ser excluido porque possui vinculos com o historico do sistema.'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, self.protected_error_message)
            return redirect(success_url)


class TenantQuerySetMixin:
    company_field = 'company'

    def get_queryset(self):
        queryset = super().get_queryset()
        return scope_queryset_for_user(queryset, self.request.user, self.company_field)


class TenantFormMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company'] = get_user_company(self.request.user)
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        if hasattr(form.instance, 'company_id') and not form.instance.company_id:
            form.instance.company = get_user_company(self.request.user)
        return super().form_valid(form)


# -- Mixins reutilizaveis --------------------------------------------------

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
    """Apenas Admin pode gerenciar usuarios."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not get_user_profile(request.user).can_manage_users():
            return _deny(request, 'Apenas administradores podem gerenciar usuarios.')
        return super().dispatch(request, *args, **kwargs)


class FuelRegisterMixin(LoginRequiredMixin):
    """Motorista, Operador, Gestor e Admin podem registrar abastecimentos."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not get_user_profile(request.user).can_register_fuel():
            return _deny(request, 'Voce nao tem permissao para registrar abastecimentos.')
        return super().dispatch(request, *args, **kwargs)


class TripRegisterMixin(LoginRequiredMixin):
    """Motorista, Operador, Gestor e Admin podem registrar viagens."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not get_user_profile(request.user).can_register_trip():
            return _deny(request, 'Voce nao tem permissao para registrar viagens.')
        return super().dispatch(request, *args, **kwargs)


class MaintenanceRegisterMixin(LoginRequiredMixin):
    """Apenas Operador e acima podem registrar manutencoes."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not get_user_profile(request.user).can_register_maintenance():
            return _deny(request, 'Voce nao tem permissao para registrar manutencoes.')
        return super().dispatch(request, *args, **kwargs)
