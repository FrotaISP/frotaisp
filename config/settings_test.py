from .settings_base import *

DEBUG = False
SECRET_KEY = 'test-secret-key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

CORS_ALLOW_ALL_ORIGINS = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
