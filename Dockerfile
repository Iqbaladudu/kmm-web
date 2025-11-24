# pull official base image
FROM python:3.11.14

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

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

# Expose port
EXPOSE 8000

# Run uvicorn directly (without uv run for production)
CMD ["uvicorn", "kmm_web_backend.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
