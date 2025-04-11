FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=9000 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        curl \
        postgresql-client \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the wait-for-postgres script and make it executable
COPY scripts/wait-for-postgres.sh /usr/local/bin/wait-for-postgres
RUN chmod +x /usr/local/bin/wait-for-postgres

# Copy application code
COPY . .

# Make sure directory structure is correct
RUN ls -la && ls -la app/

# Make scripts executable
RUN chmod +x scripts/*.sh || echo "No scripts to make executable"

# Create non-root user and switch to it
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port (Coolify will use the PORT env variable)
EXPOSE $PORT

# Set health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
  CMD curl -f http://localhost:$PORT/ || exit 1

# Create a startup script that waits for the database before starting the app
RUN echo '#!/bin/bash\n\
echo "Waiting for Postgres database..."\n\
# Extract host and user from DATABASE_URL\n\
DB_URL=$DATABASE_URL\n\
if [[ $DB_URL =~ postgresql.*://([^:]+):([^@]+)@([^:]+):([^/]+) ]]; then\n\
  DB_USER="${BASH_REMATCH[1]}"\n\
  DB_HOST="${BASH_REMATCH[3]}"\n\
  DB_PORT="${BASH_REMATCH[4]}"\n\
  echo "Extracted DB_HOST=$DB_HOST DB_PORT=$DB_PORT DB_USER=$DB_USER"\n\
  # Wait for database to be ready\n\
  wait-for-postgres "$DB_HOST" "$DB_USER"\n\
else\n\
  echo "Could not parse DATABASE_URL, skipping database wait..."\n\
fi\n\
\n\
# Debug info\n\
echo "Contents of current directory:"\n\
ls -la\n\
echo "Contents of app directory:"\n\
ls -la app/\n\
\n\
# Apply database migrations\n\
echo "Applying database migrations..."\n\
alembic upgrade head || echo "Migration failed but continuing..."\n\
\n\
# Start the application\n\
echo "Starting application..."\n\
cd /app && uvicorn app.main:app --host 0.0.0.0 --port $PORT\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]