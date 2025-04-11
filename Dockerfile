FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=9000

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc curl postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the wait-for-postgres script and make it executable
COPY scripts/wait-for-postgres.sh /usr/local/bin/wait-for-postgres
RUN chmod +x /usr/local/bin/wait-for-postgres

# Copy application code
COPY . .

# Make scripts executable
RUN chmod +x scripts/*.sh

# Create non-root user and switch to it
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port (Coolify will use the PORT env variable)
EXPOSE $PORT

# Set health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
  CMD curl -f http://localhost:$PORT/ || exit 1

# Run the application with gunicorn for production
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT