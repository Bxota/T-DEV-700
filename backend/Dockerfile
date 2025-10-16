# ---------- base ----------
ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION} AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libpq-dev libjpeg62-turbo-dev zlib1g-dev curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---------- dev ----------
FROM base AS dev
ARG PORT_BACK
ENV PORT_BACK=${PORT_BACK}

COPY . .

RUN python -m pip install --upgrade pip && \
    if [ -f requirements.txt ]; then \
        pip install -r requirements.txt; \
    else \
        echo "No requirements.txt found → installing minimal deps..." && \
        pip install Django djangorestframework djangorestframework-simplejwt psycopg[binary] gunicorn; \
    fi

EXPOSE ${PORT_BACK}
CMD ["bash", "-lc", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:${PORT_BACK}"]

# ---------- builder ----------
FROM base AS builder
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && pip install --prefix=/install -r requirements.txt || \
    (echo 'Fallback minimal deps' && pip install --prefix=/install Django djangorestframework djangorestframework-simplejwt psycopg[binary] gunicorn)
COPY . /app

# ---------- prod ----------
FROM python:${PYTHON_VERSION} AS prod
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 libjpeg62-turbo zlib1g \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=builder /install /usr/local
COPY --from=builder /app /app
ENV APP_USER=appuser
RUN adduser --disabled-password --gecos "" $APP_USER
EXPOSE ${PORT_BACK}
CMD ["sh","-lc","set -e; \
  mkdir -p /app/static; \
  chown -R $APP_USER:$APP_USER /app/static || true; \
  python manage.py migrate --noinput; \
  python manage.py collectstatic --noinput; \
  exec su -s /bin/sh -c 'gunicorn core.wsgi:application --bind 0.0.0.0:${PORT_BACK}' $APP_USER"]
