#!/bin/bash

# Production deployment script for KMM Web Application

set -e

echo "🚀 Starting production deployment..."

# Check if required environment variables are set
if [ -z "$SECRET_KEY" ]; then
    echo "❌ ERROR: SECRET_KEY environment variable is not set"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable is not set"
    exit 1
fi

if [ -z "$ALLOWED_HOSTS" ]; then
    echo "❌ ERROR: ALLOWED_HOSTS environment variable is not set"
    exit 1
fi

# Set Django environment to production
export DJANGO_ENV=production

echo "📦 Installing production dependencies..."
pip install -e .[production]

echo "🔄 Running database migrations..."
python manage.py migrate --noinput

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "✅ Creating log directories..."
mkdir -p /var/log/django
chmod 755 /var/log/django

echo "🔍 Running system checks..."
python manage.py check --deploy

echo "🧪 Running basic tests..."
python manage.py test data_management.tests --verbosity=2

echo "🎯 Creating superuser (if needed)..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', '${ADMIN_EMAIL:-admin@kmm-mesir.org}', '${ADMIN_PASSWORD:-changeme123}')
    print('Superuser created')
else:
    print('Superuser already exists')
"

echo "✅ Production deployment completed successfully!"
echo "🌐 Your application is ready to run with: gunicorn kmm_web_backend.wsgi:application"
