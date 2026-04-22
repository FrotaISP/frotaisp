from .settings_base import *

DEBUG = False

if SECRET_KEY == INSECURE_DEV_SECRET:
    raise ValueError('Defina uma SECRET_KEY segura para produção.')

if not ALLOWED_HOSTS:
    raise ValueError('Defina ALLOWED_HOSTS para produção.')

CORS_ALLOW_ALL_ORIGINS = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
