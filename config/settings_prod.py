from decouple import config

from .settings_base import *

DEBUG = False

if SECRET_KEY == INSECURE_DEV_SECRET:
    raise ValueError('Defina uma SECRET_KEY segura para produção.')

if not ALLOWED_HOSTS:
    raise ValueError('Defina ALLOWED_HOSTS para produção.')

if not DB_NAME:
    raise ValueError('Defina DB_NAME para produção.')

for env_name in ('DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT'):
    if not config(env_name, default='').strip():
        raise ValueError(f'Defina {env_name} para produção.')

CORS_ALLOW_ALL_ORIGINS = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
