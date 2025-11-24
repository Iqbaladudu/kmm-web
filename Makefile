.PHONY: help build up down restart logs shell migrate collectstatic createsuperuser backup clean

# Default target
help:
	@echo "KMM Web - Docker Management Commands"
	@echo "====================================="
	@echo ""
	@echo "Setup & Deployment:"
	@echo "  make setup          - Initial setup (copy .env, build, run)"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo ""
	@echo "Development:"
	@echo "  make logs           - View logs (all services)"
	@echo "  make logs-web       - View web service logs"
	@echo "  make logs-nginx     - View nginx logs"
	@echo "  make shell          - Django shell"
	@echo "  make bash           - Bash shell in web container"
	@echo ""
	@echo "Database:"
	@echo "  make migrate        - Run database migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make dbshell        - PostgreSQL shell"
	@echo "  make backup         - Backup database"
	@echo ""
	@echo "Static Files:"
	@echo "  make collectstatic  - Collect static files"
	@echo ""
	@echo "User Management:"
	@echo "  make createsuperuser - Create Django superuser"
	@echo ""
	@echo "Maintenance:"
	@echo "  make ps             - Show running containers"
	@echo "  make clean          - Remove containers (keep data)"
	@echo "  make clean-all      - Remove everything (including data)"
	@echo "  make rebuild        - Rebuild and restart"
	@echo ""

# Setup
setup:
	@if [ ! -f .env ]; then \
		cp .env.docker .env; \
		echo "✅ Created .env file"; \
		echo "⚠️  Please edit .env and update SECRET_KEY, POSTGRES_PASSWORD, ALLOWED_HOSTS"; \
		echo ""; \
		echo "Generate SECRET_KEY:"; \
		echo "  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"; \
	else \
		echo ".env already exists"; \
	fi
	@chmod +x docker-entrypoint.sh docker-deploy.sh
	@make build
	@make up

# Docker operations
build:
	docker-compose build

up:
	docker-compose up -d
	@echo ""
	@echo "✅ Services started!"
	@echo "🌐 Web: http://localhost"
	@echo "🔧 Admin: http://localhost/admin"
	@echo "💚 Health: http://localhost/health/"

down:
	docker-compose down

restart:
	docker-compose restart

rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

# Logs
logs:
	docker-compose logs -f

logs-web:
	docker-compose logs -f web

logs-nginx:
	docker-compose logs -f nginx

logs-postgres:
	docker-compose logs -f postgres

logs-redis:
	docker-compose logs -f redis

# Shell access
shell:
	docker-compose exec web python manage.py shell

bash:
	docker-compose exec web bash

dbshell:
	docker-compose exec postgres psql -U kmm_user -d kmm_web_db

# Django commands
migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

createsuperuser:
	docker-compose exec web python manage.py createsuperuser

check:
	docker-compose exec web python manage.py check --deploy

# Database backup
backup:
	@mkdir -p backups
	@echo "Creating backup..."
	docker-compose exec -T postgres pg_dump -U kmm_user kmm_web_db | gzip > backups/backup_$$(date +%Y%m%d_%H%M%S).sql.gz
	@echo "✅ Backup created in backups/"

# Status
ps:
	docker-compose ps

stats:
	docker stats

# Cleanup
clean:
	docker-compose down
	@echo "✅ Containers stopped and removed (data preserved)"

clean-all:
	@echo "⚠️  WARNING: This will delete ALL data including database!"
	@read -p "Are you sure? (yes/NO): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker-compose down -v; \
		echo "✅ All containers and volumes removed"; \
	else \
		echo "Cancelled"; \
	fi

clean-logs:
	rm -rf logs/*.log
	@echo "✅ Log files cleaned"

# Production deployment
deploy:
	./docker-deploy.sh

# Development
dev-setup:
	cp .env.docker .env
	@echo "Edit .env file for development, then run: make up"

