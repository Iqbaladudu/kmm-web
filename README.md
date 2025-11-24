# 🎓 KMM Web - Student Management System

Django-based web application for managing KMM (Keluarga Mahasiswa Mesir) student data with modern UI using Vite,
TypeScript, and Tailwind CSS.

## 🚀 Quick Start

### Docker Deployment (Recommended for Production)

```bash
# 1. Copy environment template
cp .env.docker .env

# 2. Generate SECRET_KEY and edit .env
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
# Edit .env with generated key and your settings

# 3. Validate and deploy
./validate-deployment.sh
./docker-deploy.sh

# 4. Create admin user
docker-compose exec web python manage.py createsuperuser
```

**Access your application:**

- 🌐 Web: http://localhost
- 🔧 Admin: http://localhost/admin
- 💚 Health: http://localhost/health/

📖 **Detailed guides:**

- [Quick Start (5 min)](DOCKER_QUICKSTART.md)
- [Complete Deployment Guide](DOCKER_DEPLOYMENT.md)
- [Implementation Summary](DOCKER_IMPLEMENTATION_SUMMARY.md)

### Local Development

```bash
# Install uv (package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Copy environment
cp .env.local.example .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development servers (in separate terminals)
python manage.py runserver  # Django
python manage.py vite dev   # Vite frontend
```

## 📦 Stack

### Backend

- **Framework**: Django 5.2+
- **Database**: PostgreSQL (production) / SQLite (development)
- **Cache**: Redis
- **Server**: Gunicorn + Nginx (production)
- **Package Manager**: uv

### Frontend

- **Build Tool**: Vite
- **Language**: TypeScript
- **CSS**: Tailwind CSS 4
- **Icons**: Font Awesome
- **Interactions**: SortableJS, NotifyX

### Infrastructure

- **Containers**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **Static Files**: WhiteNoise
- **File Storage**: Local / AWS S3

## 🏗️ Project Structure

```
kmm-web/
├── data_management/        # Main Django app
│   ├── models.py          # Student data models
│   ├── views.py           # Business logic
│   ├── forms.py           # Form handling
│   ├── admin.py           # Admin customization
│   └── templates/         # Django templates
├── kmm_web_backend/       # Django project settings
│   └── settings/          # Organized settings
│       ├── base.py        # Base configuration
│       ├── local.py       # Development settings
│       ├── production.py  # Production settings
│       ├── apps.py        # Installed apps
│       ├── database.py    # Database config
│       ├── security.py    # Security settings
│       ├── static.py      # Static files
│       └── logging.py     # Logging config
├── vite/                  # Frontend app
│   ├── src/              # TypeScript/CSS source
│   └── static/dist/      # Built assets
├── nginx/                 # Nginx configuration
│   ├── nginx.conf        # Main config
│   └── conf.d/           # Server blocks
├── templates/             # Base templates
├── staticfiles/          # Collected static files
├── media/                # User uploads
├── logs/                 # Application logs
├── Dockerfile            # Multi-stage Docker build
├── docker-compose.yml    # Services orchestration
└── Makefile             # Developer shortcuts
```

## 🔧 Management Commands

### Using Make (Recommended)

```bash
make help              # Show all available commands

# Development
make setup             # Initial setup
make up                # Start all services
make down              # Stop all services
make logs              # View logs
make shell             # Django shell
make bash              # Container bash

# Database
make migrate           # Run migrations
make makemigrations    # Create migrations
make dbshell          # PostgreSQL shell
make backup           # Backup database

# Maintenance
make ps               # Service status
make restart          # Restart services
make clean            # Remove containers
```

### Using Docker Compose

```bash
# Service management
docker-compose up -d           # Start services
docker-compose down            # Stop services
docker-compose logs -f         # View logs
docker-compose ps              # Status

# Django commands
docker-compose exec web python manage.py <command>
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py migrate

# Database backup
docker-compose exec postgres pg_dump -U kmm_user kmm_web_db > backup.sql
```

## 🔐 Environment Variables

Key variables in `.env`:

```bash
# Core Django
DJANGO_ENV=production
SECRET_KEY=<generate-this>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

# Database (auto-configured in Docker)
POSTGRES_DB=kmm_web_db
POSTGRES_USER=kmm_user
POSTGRES_PASSWORD=<secure-password>

# Redis (auto-configured in Docker)
# REDIS_URL=redis://redis:6379/1

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<app-password>
```

See `.env.docker` for complete template.

## 📚 Features

### Student Management

- ✅ Complete student profiles
- ✅ Photo uploads
- ✅ Academic information
- ✅ Financial tracking
- ✅ Contact details
- ✅ Draft/published status
- ✅ Verification workflow

### Admin Interface

- ✅ Custom admin dashboard
- ✅ Advanced filters
- ✅ Bulk actions
- ✅ Import/Export (CSV/Excel)
- ✅ Search functionality
- ✅ Inline editing

### Technical Features

- ✅ Health check endpoints
- ✅ Database connection pooling
- ✅ Redis caching
- ✅ Static file optimization
- ✅ Security headers
- ✅ Rate limiting
- ✅ Logging & monitoring
- ✅ Docker deployment

## 🔒 Security

### Production Security

- ✅ SECRET_KEY validation (50+ chars)
- ✅ DEBUG=False enforcement
- ✅ ALLOWED_HOSTS configuration
- ✅ Security headers (Nginx)
- ✅ HTTPS/SSL ready
- ✅ Rate limiting
- ✅ Non-root container user
- ✅ CSRF protection
- ✅ XSS protection

### Run Security Check

```bash
docker-compose exec web python manage.py check --deploy
```

## 📊 Monitoring

### Health Checks

- `/health/` - Overall health
- `/health/db/` - Database connectivity
- `/health/cache/` - Redis connectivity

### Logs

```bash
# Application logs
docker-compose logs -f web

# Nginx access/error logs
docker-compose logs -f nginx

# Database logs
docker-compose logs -f postgres

# All logs
docker-compose logs -f
```

### Metrics

```bash
# Container resource usage
docker stats

# Service status
docker-compose ps
make ps
```

## 🛠️ Development

### Run Tests

```bash
docker-compose exec web python manage.py test
```

### Database Shell

```bash
# PostgreSQL
docker-compose exec postgres psql -U kmm_user -d kmm_web_db

# Django ORM
docker-compose exec web python manage.py shell
```

### Frontend Development

```bash
# Vite dev server (hot reload)
docker-compose exec web python manage.py vite dev

# Build production assets
docker-compose exec web npm --prefix vite/src run build
```

## 📦 Backup & Restore

### Database Backup

```bash
# Automated via Make
make backup

# Manual
docker-compose exec -T postgres pg_dump -U kmm_user kmm_web_db | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restore Database

```bash
# Stop application
docker-compose stop web

# Restore
gunzip -c backup.sql.gz | docker-compose exec -T postgres psql -U kmm_user kmm_web_db

# Restart
docker-compose start web
```

### Media Files Backup

```bash
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

## 🚀 Deployment

### Production Deployment

1. Clone repository
2. Copy and configure `.env`
3. Run validation: `./validate-deployment.sh`
4. Deploy: `./docker-deploy.sh`
5. Configure SSL (see [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md))
6. Set up backups
7. Configure monitoring

### SSL/HTTPS Setup

```bash
# Get Let's Encrypt certificate
certbot certonly --standalone -d yourdomain.com

# Copy to nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/

# Enable SSL config
cp nginx/conf.d/ssl.conf.example nginx/conf.d/ssl.conf
# Edit and uncomment configuration

# Restart
docker-compose restart nginx
```

## 📖 Documentation

- **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)** - 5-minute deployment guide
- **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** - Complete deployment documentation
- **[DOCKER_IMPLEMENTATION_SUMMARY.md](DOCKER_IMPLEMENTATION_SUMMARY.md)** - Technical implementation details
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Traditional deployment (non-Docker)
- **[SETTINGS_ARCHITECTURE.md](SETTINGS_ARCHITECTURE.md)** - Settings organization
- **[QUICK_START.md](QUICK_START.md)** - Local development setup

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**

```bash
sudo lsof -i :80
# Change HTTP_PORT in .env
```

**Database connection error:**

```bash
docker-compose logs postgres
docker-compose restart postgres
```

**Static files not loading:**

```bash
make collectstatic
docker-compose restart nginx
```

**Permission errors:**

```bash
sudo chown -R 1000:1000 media/ logs/
```

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for more troubleshooting.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

[Add your license here]

## 👥 Authors

KMM Mesir Development Team

## 🙏 Acknowledgments

- Django community
- Vite community
- All contributors

---

**Happy Coding! 🚀**

For questions or issues, please open an issue on GitHub.

