#!/bin/sh
set -e

echo "📦 Waiting for PostgreSQL to start..."
until pg_isready -h db -p 5432 -q; do
  echo "⏳ PostgreSQL is not ready yet..."
  sleep 1
done

echo "✅ PostgreSQL is up and running."

echo "🧱 Applying Django migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "🚀 Starting Django development server..."
python manage.py runserver 0.0.0.0:8000