"""
Gunicorn configuration for KMM Web Application production deployment.
Optimized for Docker/containerized environments.
"""

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes - get from environment or calculate
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = 1000
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 30))
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging - Docker-friendly (stdout/stderr)
# In Docker, we log to stdout/stderr so Docker can collect logs
accesslog = "-"  # stdout
errorlog = "-"  # stderr
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "kmm_web_gunicorn"

# Server mechanics
daemon = False
pidfile = None  # No pidfile needed in containers
user = None
group = None
tmp_upload_dir = None

# SSL (handled by nginx reverse proxy in Docker)
# keyfile = None
# certfile = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Preload application for better performance
preload_app = True

# Worker timeout
graceful_timeout = 30

# Forwarded headers (important when behind nginx reverse proxy)
forwarded_allow_ips = "*"  # Trust all IPs since we're behind nginx in same Docker network


def when_ready(server):
    server.log.info("Server is ready. Spawning workers")


def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")


def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)
