# ---------------------------------------------------------------
# Dockerfile - Task Manager API
# Lightweight image used by the CI/CD pipeline (GitHub Actions)
# and by Minikube / a local VM for the final deployment step.
# ---------------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first so Docker can cache this layer
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/app.py .

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Use gunicorn in "production-like" mode instead of the Flask dev server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
