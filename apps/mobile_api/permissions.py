from rest_framework.permissions import BasePermission

from apps.core.mixins import get_user_profile


class IsDriverMobileUser(BasePermission):
    message = 'Acesso restrito ao app mobile de motoristas.'

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        profile = get_user_profile(user)
        return user.is_superuser or profile.is_driver
