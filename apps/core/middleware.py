# apps/core/middleware.py
from django.db import DatabaseError, OperationalError, ProgrammingError

from apps.core.mixins import get_user_company
from apps.core.models import AuditLog


class AuditLogMiddleware:
    """Registra alteracoes feitas por usuarios autenticados sem interromper a resposta."""

    WRITE_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if self._should_log(request):
            self._create_log(request, response)
        return response

    def _should_log(self, request):
        user = getattr(request, 'user', None)
        if request.method not in self.WRITE_METHODS:
            return False
        if not user or not user.is_authenticated:
            return False
        return not request.path.startswith(('/static/', '/media/'))

    def _create_log(self, request, response):
        try:
            AuditLog.objects.create(
                company=get_user_company(request.user),
                user=request.user,
                action=self._infer_action(request),
                path=request.path[:255],
                method=request.method,
                status_code=getattr(response, 'status_code', None),
                ip_address=self._get_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            )
        except (DatabaseError, OperationalError, ProgrammingError):
            pass

    def _infer_action(self, request):
        path = request.path.lower()
        if request.method == 'DELETE' or 'excluir' in path or 'delete' in path:
            return 'delete'
        if request.method in {'PUT', 'PATCH'} or 'editar' in path or 'update' in path:
            return 'update'
        if request.method == 'POST':
            return 'create'
        return 'other'

    def _get_ip(self, request):
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
