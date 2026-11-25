FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application.
COPY bot ./bot
COPY db ./db

# Run as a non-root user.
RUN useradd --create-home appuser
USER appuser

CMD ["python", "-m", "bot"]
