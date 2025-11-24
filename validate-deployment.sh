#!/bin/bash
# Pre-deployment validation script

set -e

echo "🔍 KMM Web - Pre-Deployment Validation"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

# Check Docker
echo -n "Checking Docker installation... "
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "  Docker is not installed"
    ERRORS=$((ERRORS+1))
fi

# Check Docker Compose
echo -n "Checking Docker Compose... "
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo "  Docker Compose is not installed"
    ERRORS=$((ERRORS+1))
fi

# Check .env file
echo -n "Checking .env file... "
if [ -f .env ]; then
    echo -e "${GREEN}✓${NC}"

    # Validate critical variables
    source .env

    # Check SECRET_KEY
    echo -n "  Validating SECRET_KEY... "
    if [ -z "$SECRET_KEY" ]; then
        echo -e "${RED}✗${NC}"
        echo "    SECRET_KEY is not set"
        ERRORS=$((ERRORS+1))
    elif [ "$SECRET_KEY" == "your-very-secure-secret-key-here-minimum-50-characters-CHANGE-THIS-IN-PRODUCTION" ]; then
        echo -e "${RED}✗${NC}"
        echo "    SECRET_KEY is still default value"
        ERRORS=$((ERRORS+1))
    elif [ ${#SECRET_KEY} -lt 50 ]; then
        echo -e "${YELLOW}⚠${NC}"
        echo "    SECRET_KEY is less than 50 characters"
        WARNINGS=$((WARNINGS+1))
    else
        echo -e "${GREEN}✓${NC}"
    fi

    # Check DEBUG
    echo -n "  Validating DEBUG setting... "
    if [ "$DEBUG" == "False" ] || [ "$DEBUG" == "false" ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}⚠${NC}"
        echo "    DEBUG is not set to False (current: $DEBUG)"
        WARNINGS=$((WARNINGS+1))
    fi

    # Check ALLOWED_HOSTS
    echo -n "  Validating ALLOWED_HOSTS... "
    if [ -z "$ALLOWED_HOSTS" ]; then
        echo -e "${YELLOW}⚠${NC}"
        echo "    ALLOWED_HOSTS is not set"
        WARNINGS=$((WARNINGS+1))
    elif [[ "$ALLOWED_HOSTS" == *"yourdomain.com"* ]]; then
        echo -e "${YELLOW}⚠${NC}"
        echo "    ALLOWED_HOSTS contains placeholder domain"
        WARNINGS=$((WARNINGS+1))
    else
        echo -e "${GREEN}✓${NC}"
    fi

    # Check POSTGRES_PASSWORD
    echo -n "  Validating POSTGRES_PASSWORD... "
    if [ -z "$POSTGRES_PASSWORD" ]; then
        echo -e "${RED}✗${NC}"
        echo "    POSTGRES_PASSWORD is not set"
        ERRORS=$((ERRORS+1))
    elif [ "$POSTGRES_PASSWORD" == "changeme_secure_password_here" ] || [ "$POSTGRES_PASSWORD" == "changeme" ]; then
        echo -e "${YELLOW}⚠${NC}"
        echo "    POSTGRES_PASSWORD is default/weak"
        WARNINGS=$((WARNINGS+1))
    else
        echo -e "${GREEN}✓${NC}"
    fi

else
    echo -e "${YELLOW}⚠${NC}"
    echo "  .env file not found (will use .env.docker defaults)"
    WARNINGS=$((WARNINGS+1))
fi

# Check required files
echo -n "Checking Dockerfile... "
if [ -f Dockerfile ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    ERRORS=$((ERRORS+1))
fi

echo -n "Checking docker-compose.yml... "
if [ -f docker-compose.yml ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    ERRORS=$((ERRORS+1))
fi

echo -n "Checking docker-entrypoint.sh... "
if [ -f docker-entrypoint.sh ]; then
    if [ -x docker-entrypoint.sh ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}⚠${NC}"
        echo "  docker-entrypoint.sh is not executable"
        chmod +x docker-entrypoint.sh
        echo "  Fixed: Made executable"
    fi
else
    echo -e "${RED}✗${NC}"
    ERRORS=$((ERRORS+1))
fi

# Check directories
echo -n "Checking nginx configuration... "
if [ -d nginx ] && [ -f nginx/nginx.conf ] && [ -f nginx/conf.d/default.conf ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    ERRORS=$((ERRORS+1))
fi

# Create required directories
echo -n "Checking/creating required directories... "
mkdir -p logs backups media nginx/ssl
echo -e "${GREEN}✓${NC}"

# Check package files for Vite
echo -n "Checking Vite package.json... "
if [ -f vite/src/package.json ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠${NC}"
    echo "  vite/src/package.json not found"
    WARNINGS=$((WARNINGS+1))
fi

# Summary
echo ""
echo "======================================"
echo "Summary:"
echo "  Errors: $ERRORS"
echo "  Warnings: $WARNINGS"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Ready to deploy.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review your .env file"
    echo "  2. Run: ./docker-deploy.sh"
    echo "     or: make deploy"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Validation passed with warnings.${NC}"
    echo "Please review the warnings above."
    echo ""
    echo "You can proceed with deployment if warnings are acceptable:"
    echo "  ./docker-deploy.sh  or  make deploy"
    exit 0
else
    echo -e "${RED}❌ Validation failed with $ERRORS error(s).${NC}"
    echo "Please fix the errors above before deploying."
    exit 1
fi

