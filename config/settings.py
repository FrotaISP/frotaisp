"""
Ponto de entrada compatível para seleção de settings por ambiente.
"""

from decouple import config

APP_ENV = config('APP_ENV', default='dev').strip().lower()

if APP_ENV == 'prod':
    from .settings_prod import *
else:
    from .settings_dev import *
