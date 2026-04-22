# apps/accounts/context_processors.py
from apps.core.mixins import get_user_profile


def user_profile(request):
    """Injeta o perfil do usuário logado em todos os templates."""
    if request.user.is_authenticated:
        profile = get_user_profile(request.user)
        return {'user_profile': profile}
    return {'user_profile': None}
