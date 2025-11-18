# Django Settings - Quick Reference

## 📁 Struktur File

```
settings/
├── __init__.py           # Auto-loader
├── base.py               # ⚙️  Core settings
├── apps.py               # 📦 Apps & middleware
├── database.py           # 🗄️  Database & cache
├── security.py           # 🔒 Security settings
├── static.py             # 🎨 Static & media files
├── logging.py            # 📝 Logging config
├── local.py              # 💻 Development
├── production.py         # 🚀 Production
└── README.md             # 📖 Full documentation
```

## 🎯 Dimana Mencari Setting?

| Ingin Ubah...       | File                         | Setting                    |
|---------------------|------------------------------|----------------------------|
| Tambah app baru     | `apps.py`                    | `INSTALLED_APPS`           |
| Tambah middleware   | `apps.py`                    | `MIDDLEWARE`               |
| Ubah database       | `database.py`                | `DATABASES`                |
| Ubah cache          | `database.py`                | `CACHES`                   |
| Password validation | `security.py`                | `AUTH_PASSWORD_VALIDATORS` |
| Login URL           | `security.py`                | `LOGIN_URL`                |
| Static files path   | `static.py`                  | `STATIC_ROOT`              |
| Media files path    | `static.py`                  | `MEDIA_ROOT`               |
| Logging level       | `logging.py`                 | `LOGGING`                  |
| Timezone            | `base.py`                    | `TIME_ZONE`                |
| Language            | `base.py`                    | `LANGUAGE_CODE`            |
| Email backend       | `base.py`                    | `EMAIL_BACKEND`            |
| Debug mode          | `local.py` / `production.py` | `DEBUG`                    |
| Allowed hosts       | `local.py` / `production.py` | `ALLOWED_HOSTS`            |

## 🛠️ Common Tasks

### Menambah App Baru

Edit `apps.py`:

```python
# Aplikasi pihak ketiga
THIRD_PARTY_APPS = [
    'widget_tweaks',
    'django_htmx',
    'your_new_app',  # Tambahkan di sini
]
```

### Menambah Middleware

Edit `apps.py`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # ... middleware lain
    'your_middleware.YourMiddleware',  # Tambahkan di sini
]
```

### Mengubah Database (Development)

Edit `local.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Mengubah Logging Level

Edit `logging.py`:

```python
# Untuk logger tertentu
'loggers': {
    'data_management': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',  # Ubah di sini: DEBUG, INFO, WARNING, ERROR
        'propagate': False,
    },
}
```

### Deploy ke Production

1. Set environment variables:

```bash
export DJANGO_ENV=production
export SECRET_KEY="your-long-secret-key-here"
export DATABASE_URL="postgresql://user:pass@host:port/db"
export ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
```

2. Run migrations dan collect static:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

3. Check deployment:

```bash
python manage.py check --deploy
```

## 🔍 Debugging Tips

### Lihat Setting yang Aktif

```bash
python manage.py diffsettings
```

### Lihat Environment yang Dipakai

```bash
python -c "import os; print(os.environ.get('DJANGO_ENV', 'local'))"
```

### Test Production Settings Tanpa Deploy

```bash
DJANGO_ENV=production python manage.py check --deploy
```

### Lihat Semua Logs

```bash
tail -f logs/*.log
```

## 🆘 Quick Fixes

### "SECRET_KEY not set"

```bash
# Generate secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Set di .env file
echo "SECRET_KEY=your-generated-key-here" >> .env
```

### "No module named 'xxx'"

```bash
# Install missing package
pip install xxx

# Atau jika pakai uv
uv pip install xxx
```

### "Template not found"

```bash
# Pastikan folder templates ada
mkdir -p templates

# Check TEMPLATES setting di base.py
python manage.py shell -c "from django.conf import settings; print(settings.TEMPLATES)"
```

### Logs tidak muncul

```bash
# Buat folder logs
mkdir -p logs

# Set permissions
chmod 755 logs
```

## 📚 Learn More

Lihat dokumentasi lengkap di:

- **`settings/README.md`** - Panduan lengkap
- **`SETTINGS_REORGANIZATION.md`** - Detail perubahan

---

💡 **Tip**: Bookmark file ini untuk referensi cepat!

