# SunShift Backend - FastAPI
FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
# Add backend to Python path for module resolution
ENV PYTHONPATH=/app

WORKDIR /app

# Install system dependencies for Prophet and scientific packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1001 appuser

# Copy backend source code
COPY --chown=appuser:appuser . ./backend/

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check using Python (curl not available in slim image)
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]

# Run uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
