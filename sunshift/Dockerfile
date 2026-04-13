# SunShift FastAPI Backend — Docker image
FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency manifests first (layer-cache optimisation)
COPY pyproject.toml uv.lock ./

# Install production dependencies (no dev extras)
RUN uv sync --no-dev --frozen

# Copy application source
COPY backend/ ./backend/
COPY agent/ ./agent/

EXPOSE 8000

# Run the FastAPI server
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
