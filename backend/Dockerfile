# Python 3.12 base image
FROM python:3.12-slim

# Prevent Python from writing .pyc files and ensure output is shown immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System dependencies (gcc for some packages; libpq for Postgres client libs)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create work directory
WORKDIR /app

# Install Python deps:
# 1) If a requirements.txt exists, use it (best for reproducible builds)
# 2) Otherwise, install a minimal stack for Django 5.2.7 + DRF + SimpleJWT
COPY requirements*.txt ./
RUN if [ -f requirements.txt ]; then \
      pip install -r requirements.txt; \
    else \
      pip install --no-cache-dir \
        Django==5.2.7 \
        djangorestframework \
        djangorestframework-simplejwt \
        psycopg2-binary \
        gunicorn; \
    fi

# Copy the rest of the project (will be overridden by the bind mount in compose during dev)
COPY . .

# Expose the dev port (compose maps it to the host)
EXPOSE 8000

# The actual command is defined in docker-compose.yml