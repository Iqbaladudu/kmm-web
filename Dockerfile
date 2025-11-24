# pull official base image
FROM python:3.11.14

# set work directory
WORKDIR /app

# Install Node.js for Vite build
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy lock files
COPY pyproject.toml uv.lock ./

# Synchronize dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

RUN uv add uvicorn

# copy project
COPY . .

# Build Vite assets
WORKDIR /app/vite/src
RUN npm ci && npm run build

# Return to app directory
WORKDIR /app

# Make entrypoint script executable
RUN chmod +x docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["./docker-entrypoint.sh"]

# Run uvicorn using uv run to ensure proper environment
CMD ["uv", "run", "uvicorn", "kmm_web_backend.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
