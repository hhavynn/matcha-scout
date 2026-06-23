FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code, tests, and config
COPY app/ ./app/
COPY index.py ./
COPY tests/ ./tests/
COPY pytest.ini ./

# Expose API port
EXPOSE 8000

# Run with hot-reload in development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
