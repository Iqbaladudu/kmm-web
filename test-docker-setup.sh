#!/bin/bash
# Quick test to verify Docker setup is correct

set -e

echo "🧪 Testing Docker Production Setup"
echo "=================================="
echo ""

ERRORS=0

# Test 1: Check if files exist
echo "1. Checking required files..."
FILES=(
    "Dockerfile"
    "docker-compose.yml"
    "docker-entrypoint.sh"
    "docker-deploy.sh"
    "validate-deployment.sh"
    "Makefile"
    ".env.docker"
    ".dockerignore"
    "nginx/nginx.conf"
    "nginx/conf.d/default.conf"
    "nginx/conf.d/ssl.conf.example"
    "gunicorn.conf.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file NOT FOUND"
        ERRORS=$((ERRORS+1))
    fi
done

# Test 2: Check executability
echo ""
echo "2. Checking executable permissions..."
EXECUTABLES=(
    "docker-entrypoint.sh"
    "docker-deploy.sh"
    "validate-deployment.sh"
)

for file in "${EXECUTABLES[@]}"; do
    if [ -x "$file" ]; then
        echo "  ✓ $file is executable"
    else
        echo "  ✗ $file is NOT executable"
        chmod +x "$file" 2>/dev/null && echo "    Fixed!" || ERRORS=$((ERRORS+1))
    fi
done

# Test 3: Check file syntax
echo ""
echo "3. Checking file syntax..."

# Check Dockerfile
if grep -q "FROM python:3.13-slim-bookworm" Dockerfile; then
    echo "  ✓ Dockerfile has correct base image"
else
    echo "  ✗ Dockerfile base image issue"
    ERRORS=$((ERRORS+1))
fi

# Check docker-compose.yml
if grep -q "services:" docker-compose.yml && \
   grep -q "postgres:" docker-compose.yml && \
   grep -q "redis:" docker-compose.yml && \
   grep -q "web:" docker-compose.yml && \
   grep -q "nginx:" docker-compose.yml; then
    echo "  ✓ docker-compose.yml has all services"
else
    echo "  ✗ docker-compose.yml missing services"
    ERRORS=$((ERRORS+1))
fi

# Check nginx config
if grep -q "upstream django" nginx/nginx.conf; then
    echo "  ✓ nginx.conf has Django upstream"
else
    echo "  ✗ nginx.conf missing upstream"
    ERRORS=$((ERRORS+1))
fi

# Test 4: Check documentation
echo ""
echo "4. Checking documentation..."
DOCS=(
    "README.md"
    "DOCKER_QUICKSTART.md"
    "DOCKER_DEPLOYMENT.md"
    "DOCKER_IMPLEMENTATION_SUMMARY.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        lines=$(wc -l < "$doc")
        if [ "$lines" -gt 10 ]; then
            echo "  ✓ $doc ($lines lines)"
        else
            echo "  ✗ $doc is too short"
            ERRORS=$((ERRORS+1))
        fi
    else
        echo "  ✗ $doc NOT FOUND"
        ERRORS=$((ERRORS+1))
    fi
done

# Test 5: Check directories
echo ""
echo "5. Checking directories..."
DIRS=(
    "nginx/conf.d"
    "nginx/ssl"
)

for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "  ✓ $dir exists"
    else
        echo "  ✗ $dir NOT FOUND"
        mkdir -p "$dir" 2>/dev/null && echo "    Created!" || ERRORS=$((ERRORS+1))
    fi
done

# Summary
echo ""
echo "=================================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ All tests passed!"
    echo ""
    echo "Setup is ready for deployment."
    echo ""
    echo "Next steps:"
    echo "  1. Copy .env: cp .env.docker .env"
    echo "  2. Edit .env with your configuration"
    echo "  3. Validate: ./validate-deployment.sh"
    echo "  4. Deploy: ./docker-deploy.sh"
    exit 0
else
    echo "❌ $ERRORS test(s) failed"
    echo "Please fix the issues above."
    exit 1
fi

