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
CORS_ALLOW_CREDENTIALS = False
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Lax'
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = config('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True, cast=bool)
SECURE_HSTS_PRELOAD = config('SECURE_HSTS_PRELOAD', default=True, cast=bool)
SECURE_REFERRER_POLICY = 'same-origin'
