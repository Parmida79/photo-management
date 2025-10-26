# Hugging Face Spaces Dockerfile for AI-Powered Photo Management
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_hf.txt .
RUN pip install --no-cache-dir -r requirements_hf.txt

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p uploads

# Expose port (HF Spaces uses port 7860)
EXPOSE 7860

# Run the application
CMD ["python", "hf_main.py"]

