# Production image (Python 3.12). Local tests run on the host's Python 3.9.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application.
COPY app ./app
COPY db ./db

# Default to webhook mode in containers; override via env.
CMD ["python", "-m", "app.main"]
