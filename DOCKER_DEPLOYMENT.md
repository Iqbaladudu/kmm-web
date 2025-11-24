# KMM Web - Docker Production Deployment

Complete Docker setup untuk deploy aplikasi Django KMM Web ke production environment.

## 📦 Arsitektur

Stack yang digunakan:

- **Web Server**: Nginx (reverse proxy)
- **Application Server**: Gunicorn + Django
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Frontend**: Vite (TypeScript + Tailwind CSS)

## 🚀 Quick Start

### 1. Persiapan Environment

```bash
# Copy file environment template
cp .env.docker .env

# Edit file .env dan sesuaikan dengan kebutuhan Anda
nano .env
```

**PENTING**: Update minimal nilai berikut di `.env`:

- `SECRET_KEY` - Generate dengan:
  `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- `POSTGRES_PASSWORD` - Password database yang aman
- `ALLOWED_HOSTS` - Domain production Anda
- `EMAIL_*` - Konfigurasi email SMTP

### 2. Build dan Run

```bash
# Build semua services
docker-compose build

# Start semua services
docker-compose up -d

# Lihat logs
docker-compose logs -f
```

### 3. Setup Initial Data

```bash
# Buat superuser untuk admin
docker-compose exec web python manage.py createsuperuser

# Atau set environment variable di .env:
# DJANGO_SUPERUSER_USERNAME=admin
# DJANGO_SUPERUSER_EMAIL=admin@example.com
# DJANGO_SUPERUSER_PASSWORD=secure-password
# Lalu restart: docker-compose restart web
```

### 4. Akses Aplikasi

- **Web**: http://localhost atau http://your-domain.com
- **Admin**: http://localhost/admin
- **Health Check**: http://localhost/health/

## 🔧 Konfigurasi

### Struktur File

```
.
├── Dockerfile                 # Multi-stage build (frontend + backend)
├── docker-compose.yml         # Orchestration semua services
├── docker-entrypoint.sh       # Startup script (migrations, collectstatic)
├── .env                       # Environment variables (copy dari .env.docker)
├── gunicorn.conf.py          # Gunicorn configuration
├── nginx/
│   ├── nginx.conf            # Main nginx config
│   └── conf.d/
│       └── default.conf      # Server block configuration
└── backups/                  # PostgreSQL backups (optional)
```

### Services

#### 1. PostgreSQL (`postgres`)

- Port: 5432 (internal only)
- Volume: `postgres_data` (persistent)
- Healthcheck: pg_isready

#### 2. Redis (`redis`)

- Port: 6379 (internal only)
- Volume: `redis_data` (persistent)
- Memory limit: 256MB dengan LRU eviction

#### 3. Django Web (`web`)

- Port: 8000 (internal only, proxied by nginx)
- Volumes:
    - `static_volume` - Static files
    - `media_volume` - User uploads
    - `./logs` - Application logs
- Healthcheck: curl http://localhost:8000/health/

#### 4. Nginx (`nginx`)

- Ports: 80 (HTTP), 443 (HTTPS)
- Volumes:
    - `./nginx/nginx.conf` - Main config
    - `./nginx/conf.d/` - Server blocks
    - `static_volume` - Serve static files
    - `media_volume` - Serve media files
    - `./nginx/ssl/` - SSL certificates (optional)

## 📝 Management Commands

### Menjalankan Django Commands

```bash
# Shell
docker-compose exec web python manage.py shell

# Migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Collectstatic (jika perlu manual)
docker-compose exec web python manage.py collectstatic --noinput

# Custom management commands
docker-compose exec web python manage.py <command>
```

### Database Management

```bash
# Backup database
docker-compose exec postgres pg_dump -U kmm_user kmm_web_db > ./backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
docker-compose exec -T postgres psql -U kmm_user kmm_web_db < ./backups/backup_file.sql

# PostgreSQL shell
docker-compose exec postgres psql -U kmm_user -d kmm_web_db
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f postgres

# Tail last 100 lines
docker-compose logs --tail=100 web
```

## 🔒 SSL/HTTPS Setup

### Option 1: Let's Encrypt (Certbot)

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates to nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/

# Update nginx/conf.d/default.conf untuk enable HTTPS
# Uncomment SSL configuration block
```

### Option 2: Self-Signed Certificate (Development)

```bash
# Generate self-signed certificate
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/C=ID/ST=Jakarta/L=Jakarta/O=KMM/CN=localhost"
```

Lalu tambahkan di `nginx/conf.d/default.conf`:

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # ... rest of config
}
```

## 🔄 Updates & Maintenance

### Update Application Code

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose build web
docker-compose up -d web

# Run migrations if needed
docker-compose exec web python manage.py migrate
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart web
docker-compose restart nginx
```

### Scale Workers (if needed)

```bash
# Scale web workers
docker-compose up -d --scale web=3
```

## 📊 Monitoring

### Health Checks

- `/health/` - Overall application health
- `/health/db/` - Database connectivity
- `/health/cache/` - Redis connectivity

### Resource Usage

```bash
# Container stats
docker stats

# Specific container
docker stats kmm_web

# Disk usage
docker system df
```

## 🧹 Cleanup

### Remove Containers (Keep Data)

```bash
docker-compose down
```

### Remove Everything (Including Volumes)

```bash
# WARNING: This will delete all data!
docker-compose down -v
```

### Prune Unused Resources

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a --volumes
```

## 🐛 Troubleshooting

### Service tidak start

```bash
# Check logs
docker-compose logs web

# Check if port already in use
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

### Database connection error

```bash
# Check postgres is running
docker-compose ps postgres

# Check postgres logs
docker-compose logs postgres

# Verify DATABASE_URL in .env
docker-compose exec web env | grep DATABASE_URL
```

### Static files tidak muncul

```bash
# Collectstatic ulang
docker-compose exec web python manage.py collectstatic --noinput --clear

# Check nginx logs
docker-compose logs nginx

# Verify volume mounted
docker-compose exec nginx ls -la /app/staticfiles/
```

### Permission errors

```bash
# Fix file permissions
sudo chown -R 1000:1000 logs/
sudo chown -R 1000:1000 media/
```

## 🚀 Production Best Practices

### Security Checklist

- ✅ Set strong `SECRET_KEY` (minimum 50 characters)
- ✅ Set `DEBUG=False`
- ✅ Configure proper `ALLOWED_HOSTS`
- ✅ Use strong database password
- ✅ Enable HTTPS/SSL
- ✅ Set up firewall (ufw/iptables)
- ✅ Regular backups
- ✅ Update dependencies regularly

### Performance Tips

1. **Database Connection Pooling** - Already configured in Django settings
2. **Redis Caching** - Enabled by default
3. **Static File Serving** - Nginx serves directly (fast!)
4. **Gzip Compression** - Enabled in nginx config
5. **Worker Tuning** - Adjust `GUNICORN_WORKERS` based on CPU cores

### Backup Strategy

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=./backups
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker-compose exec -T postgres pg_dump -U kmm_user kmm_web_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Media files backup
tar -czf $BACKUP_DIR/media_$DATE.tar.gz media/

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Performance Tuning](https://www.nginx.com/blog/tuning-nginx/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 📞 Support

Jika ada masalah, check:

1. Logs dengan `docker-compose logs -f`
2. Health check endpoints
3. Environment variables di `.env`
4. Network connectivity antar containers

---

**Happy Deploying! 🎉**

