FROM python:3.12-slim

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY transcribe.py .
COPY transcribe_api.py .

# Create directories for audio files and outputs
RUN mkdir -p /app/audio /app/output

# Default command (can be overridden)
CMD ["python", "transcribe.py"]
