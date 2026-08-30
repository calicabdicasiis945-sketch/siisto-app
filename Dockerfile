FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
# Dummy key only used during docker build (collectstatic) — overridden at runtime by Railway env var
ENV SECRET_KEY=django-build-time-placeholder-key-not-used-in-production
ENV DEBUG=False

WORKDIR /app

# Install system dependencies for build, PostgreSQL, and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install via python -m pip
COPY requirements.txt /app/
RUN python -m pip install --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Collect static files during build (ignore errors for missing media/dirs)
RUN python manage.py collectstatic --noinput --clear 2>&1 || true

# Expose default port
EXPOSE 8000

# Run migrations, seed if needed, and start gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py seed_exercise_library --skip-if-exists 2>/dev/null || true && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4 --timeout 120 --forwarded-allow-ips='*' --log-file -"]
