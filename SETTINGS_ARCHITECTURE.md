# Django Settings Architecture - Visual Guide

## 🏗️ Struktur Settings

```
kmm_web_backend/settings/
│
├── __init__.py              # 🚪 Entry point - auto-detect environment
│   ├─→ local.py (default)
│   └─→ production.py (if DJANGO_ENV=production)
│
├── base.py                  # ⚙️  Core Settings (106 lines)
│   ├── Paths & BASE_DIR
│   ├── SECRET_KEY
│   ├── Core Django (ROOT_URLCONF, WSGI, etc)
│   ├── Internationalization (id, Asia/Jakarta)
│   ├── Email defaults
│   └── Import & configure:
│       ├─→ apps.py
│       ├─→ database.py
│       ├─→ security.py
│       ├─→ static.py
│       └─→ logging.py
│
├── apps.py                  # 📦 Applications (58 lines)
│   ├── DJANGO_APPS (admin, auth, etc)
│   ├── THIRD_PARTY_APPS (widget_tweaks, django_htmx)
│   ├── LOCAL_APPS (data_management, vite)
│   ├── MIDDLEWARE (10 middleware dalam urutan yang benar)
│   └── TEMPLATES (DjangoTemplates config)
│
├── database.py              # 🗄️  Database & Cache (23 lines)
│   ├── DATABASES (default: SQLite)
│   ├── CACHES (default: LocMemCache)
│   └── SESSION (db-based, 24 hours)
│
├── security.py              # 🔒 Security (46 lines)
│   ├── AUTH_PASSWORD_VALIDATORS (4 validators)
│   ├── Authentication URLs (LOGIN, LOGOUT)
│   ├── CSRF settings
│   ├── Session security
│   ├── HSTS settings
│   └── Content security headers
│
├── static.py                # 🎨 Static & Media Files (24 lines)
│   ├── STATIC_URL & STATIC_ROOT
│   ├── MEDIA_URL & MEDIA_ROOT
│   └── STORAGES (Whitenoise for staticfiles)
│
├── logging.py               # 📝 Logging (115 lines)
│   ├── Formatters (verbose, simple, json)
│   ├── Filters (require_debug_true/false)
│   ├── Handlers (console, file, error_file, security_file)
│   └── Loggers (django, django.request, data_management, etc)
│
├── local.py                 # 💻 Development (109 lines)
│   ├── DEBUG = True
│   ├── ALLOWED_HOSTS = ['*']
│   ├── SQLite database
│   ├── Dummy cache
│   ├── Console email backend
│   ├── Relaxed security (no HTTPS)
│   └── DEBUG level logging
│
└── production.py            # 🚀 Production (174 lines)
    ├── DEBUG = False
    ├── ALLOWED_HOSTS validation
    ├── PostgreSQL (via DATABASE_URL)
    ├── Redis cache (optional)
    ├── SMTP email
    ├── Strict security (HTTPS, HSTS)
    ├── WARNING level logging
    └── Template caching
```

## 🔄 Settings Flow

```
Django starts
     │
     ├─→ Load kmm_web_backend/settings/__init__.py
     │        │
     │        ├─→ Check DJANGO_ENV
     │        │
     │        ├─→ if 'production': import production.py
     │        │                           │
     │        │                           ├─→ Import base.py
     │        │                           │        │
     │        │                           │        ├─→ Import apps.py ✓
     │        │                           │        ├─→ Import database.py ✓
     │        │                           │        ├─→ Import security.py ✓
     │        │                           │        ├─→ Import static.py ✓
     │        │                           │        ├─→ Import logging.py ✓
     │        │                           │        └─→ Post-import config ✓
     │        │                           │
     │        │                           └─→ Override for production ✓
     │        │                                  ├─→ DEBUG = False
     │        │                                  ├─→ PostgreSQL
     │        │                                  ├─→ Strict security
     │        │                                  └─→ Template caching
     │        │
     │        └─→ else (default): import local.py
     │                               │
     │                               ├─→ Import base.py
     │                               │        │
     │                               │        └─→ (same as above)
     │                               │
     │                               └─→ Override for development ✓
     │                                      ├─→ DEBUG = True
     │                                      ├─→ SQLite
     │                                      ├─→ Relaxed security
     │                                      └─→ Verbose logging
     │
     └─→ Django ready! 🎉
```

## 📊 Settings Comparison

| Setting              | Development (local.py) | Production (production.py)     |
|----------------------|------------------------|--------------------------------|
| **DEBUG**            | ✅ True                 | ❌ False                        |
| **ALLOWED_HOSTS**    | ['*']                  | From env var (validated)       |
| **Database**         | SQLite (db.sqlite3)    | PostgreSQL (DATABASE_URL)      |
| **Cache**            | DummyCache             | Redis (or DummyCache fallback) |
| **Email**            | Console backend        | SMTP backend                   |
| **Session Cookie**   | Secure: False          | Secure: True                   |
| **CSRF Cookie**      | Secure: False          | Secure: True                   |
| **SSL Redirect**     | False                  | True                           |
| **HSTS**             | 0 seconds              | 31,536,000 seconds (1 year)    |
| **Logging Level**    | DEBUG                  | WARNING                        |
| **Template Caching** | ❌ No                   | ✅ Yes                          |
| **Static Files**     | StaticFilesStorage     | Whitenoise (compressed)        |

## 🎯 Import Chain

```
1. base.py imports apps.py
   └─→ Gets: INSTALLED_APPS, MIDDLEWARE, TEMPLATES

2. base.py imports database.py
   └─→ Gets: DATABASES, CACHES, SESSION settings

3. base.py imports security.py
   └─→ Gets: AUTH_PASSWORD_VALIDATORS, LOGIN_URL, CSRF, etc

4. base.py imports static.py
   └─→ Gets: STATIC_URL, MEDIA_URL, STORAGES

5. base.py imports logging.py
   └─→ Gets: LOGGING configuration

6. base.py post-import configuration
   └─→ Sets: Paths using BASE_DIR

7. local.py or production.py imports base.py
   └─→ Gets: Everything from steps 1-6

8. local.py or production.py overrides
   └─→ Customizes for specific environment
```

## 📁 File Responsibility Matrix

| File            | Lines   | Responsible For                       |
|-----------------|---------|---------------------------------------|
| `__init__.py`   | 12      | Environment detection & auto-import   |
| `base.py`       | 106     | Paths, core settings, orchestration   |
| `apps.py`       | 58      | Apps, middleware, templates           |
| `database.py`   | 23      | Database, cache, session              |
| `security.py`   | 46      | Auth, passwords, security headers     |
| `static.py`     | 24      | Static files, media files, storage    |
| `logging.py`    | 115     | Logging handlers, formatters, loggers |
| `local.py`      | 109     | Development overrides                 |
| `production.py` | 174     | Production overrides & validations    |
| **TOTAL**       | **667** | Complete Django settings              |

## 🔍 How to Find Settings

### Method 1: By Category

```python
# Want to change apps?          → apps.py
# Want to change database?       → database.py → local.py/production.py
# Want to change security?       → security.py → local.py/production.py
# Want to change static files?   → static.py
# Want to change logging?        → logging.py → local.py/production.py
```

### Method 2: By Environment

```python
# Development only?   → local.py
# Production only?    → production.py
# Both?               → base.py or category files
```

### Method 3: By Purpose

```python
# Adding new app?              → apps.py → INSTALLED_APPS
# Adding middleware?           → apps.py → MIDDLEWARE
# Changing timezone?           → base.py → TIME_ZONE
# Changing log level?          → logging.py → LOGGING['loggers']
# Adding password validator?   → security.py → AUTH_PASSWORD_VALIDATORS
```

## 💡 Design Principles

1. **Separation of Concerns**: Setiap file punya tanggung jawab yang jelas
2. **DRY (Don't Repeat Yourself)**: Shared settings di base.py dan category files
3. **Environment-Specific**: local.py dan production.py hanya berisi overrides
4. **Self-Documenting**: Extensive comments dan docstrings
5. **Fail-Safe**: Validations di production.py untuk prevent mistakes
6. **Flexible**: Mudah menambah environment baru (staging.py, testing.py)

---

**Dibuat**: 18 November 2025  
**Python**: 3.13  
**Django**: 5.2.4  
**Status**: ✅ Tested & Working

