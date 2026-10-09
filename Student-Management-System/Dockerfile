# Use official lightweight Python runtime
FROM python:3.11-slim

# Set environment variables for optimized execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000

# Set working directory inside container
WORKDIR /app

# Copy requirements file first to take advantage of Docker layer caching
COPY requirements.txt .

# Install dependencies without caching pip wheels to keep image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into container
COPY backend ./backend
COPY frontend ./frontend
COPY run.py .

# Expose port for FastAPI backend & static Web UI
EXPOSE 8000

# Run the app entrypoint (auto-seeds database if needed and starts Uvicorn)
CMD ["python", "run.py"]

