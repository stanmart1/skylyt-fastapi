# Multi-stage build for production
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies globally
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY --from=builder /app /app

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Create storage directories and set permissions AFTER copying files
RUN mkdir -p /app/storage/hotels /app/storage/cars /app/storage/general /app/storage/payment_proofs /app/storage/documents \
    && chown -R app:app /app \
    && chmod -R 755 /app/storage

# Expose port
EXPOSE 8000

# Health check (dummy: always returns 200 OK)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD echo "OK" || exit 1

# Entrypoint fixes storage permissions (for mounted volumes) then drops to app user
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]