# ============================================================================
# Stage 1: Build Vite Frontend Assets
# ============================================================================
FROM node:20-slim AS frontend-builder

WORKDIR /app/vite

# Copy package files for vite
COPY vite/src/package.json vite/src/package-lock.json* ./

# Install node dependencies
RUN npm ci --only=production

# Copy vite source files
COPY vite/src ./

# Build production assets
RUN npm run build

# ============================================================================
# Stage 2: Python Dependencies and Application
# ============================================================================
FROM python:3.13-slim-bookworm AS python-builder

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Download and install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies (production only)
RUN uv sync --locked --no-dev

# ============================================================================
# Stage 3: Final Production Image
# ============================================================================
FROM python:3.13-slim-bookworm

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for running the application
RUN useradd -m -u 1000 -s /bin/bash appuser

WORKDIR /app

# Copy Python virtual environment from builder
COPY --from=python-builder /app/.venv /app/.venv

# Copy built frontend assets from frontend-builder
COPY --from=frontend-builder /app/vite/dist /app/vite/static/dist

# Copy application code
COPY --chown=appuser:appuser . .

# Create directories for static files, media files, and logs
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R appuser:appuser /app/staticfiles /app/media /app/logs

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=kmm_web_backend.settings

# Copy entrypoint script
COPY --chown=appuser:appuser docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Use entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command (can be overridden)
CMD ["gunicorn", "kmm_web_backend.wsgi:application", "--config", "gunicorn.conf.py"]
