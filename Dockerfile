# Use Python base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]