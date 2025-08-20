# KMM Web Application - Production Deployment Guide

## 📋 Overview

This guide provides comprehensive instructions for deploying the KMM Web Application in a production environment with proper security, performance, and monitoring configurations.

## 🏗️ Architecture

### Production Stack
- **Web Server**: Nginx (reverse proxy)
- **Application Server**: Gunicorn with Django
- **Database**: PostgreSQL
- **Cache**: Redis
- **Static Files**: WhiteNoise + CDN (optional)
- **File Storage**: Local filesystem or AWS S3
- **Monitoring**: Health checks + Sentry (optional)

## 🔧 Prerequisites

### System Requirements
- Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- Python 3.13+
- PostgreSQL 13+
- Redis 6+
- Nginx
- SSL Certificate (Let's Encrypt recommended)

### Required Environment Variables
```bash
# Core Django Settings
DJANGO_ENV=production
SECRET_KEY=your-very-secure-secret-key-here-minimum-50-characters
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/kmm_web_db

# Cache
REDIS_URL=redis://localhost:6379/1

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@kmm-mesir.org

# Admin
ADMIN_EMAIL=admin@kmm-mesir.org
ADMIN_PASSWORD=secure-admin-password

# Optional: AWS S3
USE_S3=False
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name

# Optional: Monitoring
SENTRY_DSN=your-sentry-dsn-url
```

## 🚀 Deployment Steps

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3.13 python3.13-venv python3.13-dev \
    postgresql postgresql-contrib redis-server nginx \
    build-essential libpq-dev git curl

# Create application user
sudo adduser --system --group --home /var/www/kmm-web www-data
sudo mkdir -p /var/www/kmm-web
sudo chown www-data:www-data /var/www/kmm-web
```

### 2. Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

-- In PostgreSQL shell:
CREATE DATABASE kmm_web_db;
CREATE USER kmm_web_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE kmm_web_db TO kmm_web_user;
ALTER USER kmm_web_user CREATEDB;
\q
```

### 3. Application Deployment

```bash
# Switch to application user
sudo -u www-data -i

# Clone repository
cd /var/www/kmm-web
git clone https://github.com/yourusername/kmm-web.git .

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -e .[production]

# Copy environment file
cp .env.production.example .env.production
# Edit .env.production with your actual values
nano .env.production
```

### 4. Application Configuration

```bash
# Set correct permissions
sudo chown -R www-data:www-data /var/www/kmm-web
sudo chmod -R 755 /var/www/kmm-web

# Create log directories
sudo mkdir -p /var/log/django
sudo chown www-data:www-data /var/log/django
sudo chmod 755 /var/log/django

# Run deployment script
sudo -u www-data -i
cd /var/www/kmm-web
source venv/bin/activate
./deploy.sh
```

### 5. Systemd Service Setup

```bash
# Copy service file
sudo cp /var/www/kmm-web/kmm-web.service /etc/systemd/system/

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable kmm-web
sudo systemctl start kmm-web
sudo systemctl status kmm-web
```

### 6. Nginx Configuration

Create `/etc/nginx/sites-available/kmm-web`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Static Files
    location /static/ {
        alias /var/www/kmm-web/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media Files
    location /media/ {
        alias /var/www/kmm-web/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Health Checks (no auth required)
    location ~ ^/(health|ready|alive)/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Security
    client_max_body_size 10M;
    server_tokens off;
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/kmm-web /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
sudo systemctl enable certbot.timer
```

## 🔍 Monitoring & Health Checks

### Health Check Endpoints
- `https://yourdomain.com/health/` - Full health check (database, cache)
- `https://yourdomain.com/ready/` - Readiness check (migrations)
- `https://yourdomain.com/alive/` - Liveness check (basic)

### Log Monitoring
```bash
# Application logs
sudo tail -f /var/log/django/django.log
sudo tail -f /var/log/django/gunicorn_access.log
sudo tail -f /var/log/django/gunicorn_error.log

# System logs
sudo journalctl -u kmm-web -f
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🔄 Deployment Updates

```bash
#!/bin/bash
# Update script (save as update.sh)

set -e

echo "🔄 Updating KMM Web Application..."

cd /var/www/kmm-web
sudo -u www-data git pull origin main
sudo -u www-data source venv/bin/activate && pip install -e .[production]
sudo -u www-data python manage.py migrate --noinput
sudo -u www-data python manage.py collectstatic --noinput --clear

sudo systemctl restart kmm-web
sudo systemctl reload nginx

echo "✅ Update completed!"
```

## 🔒 Security Checklist

- [ ] SECRET_KEY is set and secure (50+ characters)
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS properly configured
- [ ] SSL/HTTPS enabled with strong ciphers
- [ ] Database credentials secured
- [ ] File permissions properly set
- [ ] Security headers configured
- [ ] Regular security updates scheduled
- [ ] Monitoring and alerting configured
- [ ] Backup strategy implemented

## 🚨 Troubleshooting

### Common Issues

1. **Application won't start**
   ```bash
   sudo systemctl status kmm-web
   sudo journalctl -u kmm-web --lines 50
   ```

2. **Database connection issues**
   ```bash
   sudo -u www-data python manage.py dbshell
   ```

3. **Static files not loading**
   ```bash
   sudo -u www-data python manage.py collectstatic --clear
   sudo systemctl restart kmm-web
   ```

4. **Permission issues**
   ```bash
   sudo chown -R www-data:www-data /var/www/kmm-web
   sudo chmod -R 755 /var/www/kmm-web
   ```

## 🔧 Performance Tuning

### Database Optimization
```sql
-- In PostgreSQL, adjust these settings in postgresql.conf:
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
```

### Redis Configuration
```bash
# In /etc/redis/redis.conf:
maxmemory 512mb
maxmemory-policy allkeys-lru
```

### Gunicorn Workers
Adjust workers in `gunicorn.conf.py` based on server resources:
```python
workers = (2 * CPU_COUNT) + 1
```

## 📊 Monitoring Integration

### Sentry Setup (Optional)
1. Create Sentry project
2. Add SENTRY_DSN to .env.production
3. Restart application

### Custom Monitoring
Create custom monitoring scripts to check:
- Application response time
- Database performance
- Disk usage
- Memory usage
- SSL certificate expiration

## 🔄 Backup Strategy

### Database Backup
```bash
#!/bin/bash
# Daily backup script
pg_dump kmm_web_db | gzip > /backups/kmm_web_$(date +%Y%m%d).sql.gz
```

### File Backup
```bash
#!/bin/bash
# Weekly file backup
tar -czf /backups/kmm_web_files_$(date +%Y%m%d).tar.gz /var/www/kmm-web/media/
```

## 📞 Support

For production support and issues:
- Check logs first: `/var/log/django/`
- Use health check endpoints for monitoring
- Monitor system resources (CPU, memory, disk)
- Keep backups current
- Follow security best practices

---

**Note**: Replace all placeholder values (yourdomain.com, passwords, etc.) with your actual production values.
