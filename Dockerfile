# Use a slim Python base
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Upgrade pip and install packaging/build helpers
RUN pip install --no-cache-dir --upgrade pip build setuptools wheel

# Copy pyproject (and optional lockfile) first to leverage Docker layer caching
COPY pyproject.toml poetry.lock* /app/

# Install the project and its dependencies from pyproject.toml (PEP 517)
RUN pip install --no-cache-dir .

# Copy the rest of the source
COPY . /app

# Expose port (optional)
EXPOSE 8000

# Default command — adjust import target to your app (e.g. main:app or src.main:app)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]