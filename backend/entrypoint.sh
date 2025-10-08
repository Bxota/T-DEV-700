#!/bin/sh
set -e

echo "📦 Waiting for PostgreSQL to start..."
until pg_isready -h db -p 5432 -q; do
  echo "⏳ PostgreSQL is not ready yet..."
  sleep 1
done

echo "✅ PostgreSQL is up and running."

echo "🧱 Applying Django migrations..."
python manage.py migrate --noinput

python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model

email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
first_name = os.environ.get("DJANGO_SUPERUSER_FIRST_NAME", "Admin")
last_name = os.environ.get("DJANGO_SUPERUSER_LAST_NAME", "User")

if email and password:
    Users = get_user_model()
    if not Users.objects.filter(email=email).exists():
        Users.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        print(f"[init] Superuser créé: {email}")
    else:
        print(f"[init] Superuser déjà présent: {email}")
else:
    print("[init] Variables DJANGO_SUPERUSER_EMAIL/PASSWORD manquantes, skip.")
PY

echo "🚀 Starting Django development server..."
python manage.py runserver 0.0.0.0:8000