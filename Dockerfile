# Production Dockerfile (Render compatible) using ASGI + Daphne
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Install system deps (optional: psycopg2 build deps cleaned afterwards)
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Collect static during image build (ok to ignore if migrations not applied yet)
RUN python manage.py collectstatic --noinput || true
ENV PORT=8000
EXPOSE 8000
CMD ["daphne", "-b", "0.0.0.0", "-p", "${PORT}", "managementProject.asgi:application"]
