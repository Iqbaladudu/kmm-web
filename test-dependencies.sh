#!/bin/bash
# Test script to verify dependencies are installed correctly

set -e

echo "🧪 Testing Dependencies Installation..."
echo ""

# Activate virtual environment
export VIRTUAL_ENV=/app/.venv
export PATH="/app/.venv/bin:$PATH"

echo "📍 Python location: $(which python)"
echo "📍 Python version: $(python --version)"
echo ""

# Test critical dependencies
echo "Testing critical dependencies..."

dependencies=(
    "psycopg"
    "django"
    "gunicorn"
    "uvicorn"
    "whitenoise"
    "sentry_sdk"
)

for dep in "${dependencies[@]}"; do
    if python -c "import $dep" 2>/dev/null; then
        version=$(python -c "import $dep; print(getattr($dep, '__version__', 'unknown'))")
        echo "✅ $dep ($version)"
    else
        echo "❌ $dep - NOT FOUND"
        exit 1
    fi
done

echo ""
echo "✅ All dependencies installed correctly!"

