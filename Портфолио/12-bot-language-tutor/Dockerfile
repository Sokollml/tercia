FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application.
COPY app ./app
COPY db ./db
COPY main.py ./

# Run as a non-root user.
RUN useradd --create-home --uid 1000 tutor && chown -R tutor:tutor /app
USER tutor

CMD ["python", "main.py"]
