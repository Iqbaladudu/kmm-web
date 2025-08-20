"""
Local development settings for kmm_web_backend project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Development hosts - W020 fix
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Development SECRET_KEY - W009 fix (generate a proper one for dev)
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-that-is-long-enough-and-secure-for-development-use-only-change-in-production-50-chars-minimum')

# Add development-only apps
INSTALLED_APPS += [
    'django_browser_reload',
]

# Add development middleware
MIDDLEWARE.append('django_browser_reload.middleware.BrowserReloadMiddleware')

# Database - SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Development email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable security features for development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Enhanced logging for development
LOGGING['handlers']['console']['formatter'] = 'verbose'
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['root']['level'] = 'DEBUG'

# Development cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# File storage for development
STORAGES["default"]["BACKEND"] = "django.core.files.storage.FileSystemStorage"
STORAGES["staticfiles"]["BACKEND"] = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Django Debug Toolbar (optional - uncomment if you want to use it)
# if 'django_debug_toolbar' in INSTALLED_APPS:
#     MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
#     INTERNAL_IPS = ['127.0.0.1']
