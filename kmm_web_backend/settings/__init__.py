"""
Django settings module.
Import from local settings by default, or production if DJANGO_ENV is set to 'production'
"""
import os

env = os.environ.get('DJANGO_ENV', 'local')

if env == 'production':
    from .production import *
else:
    from .local import *
