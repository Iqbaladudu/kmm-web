# 🚀 Quick Start - Docker Deployment

## Langkah Deployment (5 Menit)

### 1. Setup Environment

```bash
# Copy template environment
cp .env.docker .env

# Generate SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Edit .env dan update:
# - SECRET_KEY (hasil generate di atas)
# - POSTGRES_PASSWORD (password aman)
# - ALLOWED_HOSTS (domain production Anda)
nano .env
```

### 2. Deploy Otomatis

```bash
# Jalankan script deployment
./docker-deploy.sh
```

### 3. Akses Aplikasi

- **Web**: http://localhost
- **Admin**: http://localhost/admin
- **Health**: http://localhost/health/

### 4. Buat Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

## 🎯 Command Penting

```bash
# Lihat logs semua services
docker-compose logs -f

# Lihat logs web saja
docker-compose logs -f web

# Stop semua services
docker-compose down

# Restart services
docker-compose restart

# Django shell
docker-compose exec web python manage.py shell

# Backup database
docker-compose exec postgres pg_dump -U kmm_user kmm_web_db > backup.sql

# Service status
docker-compose ps
```

## 📁 File Yang Dibuat

```
✅ Dockerfile                    - Multi-stage build (Vite + Django)
✅ docker-compose.yml            - Orchestration (nginx, web, postgres, redis)
✅ docker-entrypoint.sh          - Startup script (migrations, collectstatic)
✅ docker-deploy.sh              - Deployment automation script
✅ .env.docker                   - Environment template
✅ .dockerignore                 - Docker build ignore
✅ nginx/nginx.conf              - Main nginx config
✅ nginx/conf.d/default.conf     - HTTP server block
✅ nginx/conf.d/ssl.conf.example - HTTPS template
✅ DOCKER_DEPLOYMENT.md          - Complete documentation
```

## 🔧 Troubleshooting Cepat

### Port sudah digunakan

```bash
# Check port 80
sudo lsof -i :80

# Gunakan port lain
# Edit .env:
HTTP_PORT=8080
HTTPS_PORT=8443
```

### Database connection error

```bash
# Restart postgres
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Static files tidak muncul

```bash
# Re-collect static files
docker-compose exec web python manage.py collectstatic --noinput --clear

# Restart nginx
docker-compose restart nginx
```

## 📚 Dokumentasi Lengkap

Lihat **DOCKER_DEPLOYMENT.md** untuk:

- SSL/HTTPS setup
- Backup strategy
- Performance tuning
- Monitoring
- Security checklist
- Production best practices

---

**Selamat! Aplikasi Anda siap production! 🎉**

