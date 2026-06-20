FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create static files directory and collect static
RUN mkdir -p staticfiles media && \
    python manage.py collectstatic --noinput || true

# Run gunicorn
CMD ["gunicorn", "qorgo.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
