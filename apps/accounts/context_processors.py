# apps/accounts/context_processors.py
from apps.core.mixins import get_user_profile


def user_profile(request):
    """Injeta o perfil do usuário e o contador de notificações não lidas em todos os templates."""
    if request.user.is_authenticated:
        profile = get_user_profile(request.user)
        nao_lidas = request.user.notificacoes.filter(lida=False).count()
        return {
            'user_profile': profile,
            'notificacoes_nao_lidas': nao_lidas,
        }
    return {
        'user_profile': None,
        'notificacoes_nao_lidas': 0,
    }
