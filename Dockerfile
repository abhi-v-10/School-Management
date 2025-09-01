# Optional Dockerfile for Vercel / other platforms using ASGI + Daphne
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Collect static (ignore errors if DB not ready)
RUN python manage.py collectstatic --noinput || true
EXPOSE 8000
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "managementProject.asgi:application"]
