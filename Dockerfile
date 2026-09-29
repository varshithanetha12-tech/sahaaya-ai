# ==============================================================================
# Sahaaya AI Platform — Production Docker Container
# Lightweight, hardened Python 3.12 image for web cloud deployment
# ==============================================================================
FROM python:3.12-slim

# Set environment defaults
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0 \
    ENV=production \
    DATA_DIR=/app/data

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Ensure data directory exists
RUN mkdir -p /app/data && chmod -R 777 /app/data

# Expose standard port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import httpx; r = httpx.get('http://127.0.0.1:' + str(os.environ.get('PORT', 8000)) + '/health'); exit(0 if r.status_code == 200 else 1)"

# Start production server
CMD ["python", "run.py"]
