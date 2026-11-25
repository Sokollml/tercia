FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application.
COPY bot ./bot
COPY data ./data
COPY db ./db

# Persist the SQLite database (when DB_ENGINE=sqlite) outside the image.
VOLUME ["/app/data"]

CMD ["python", "-m", "bot"]
