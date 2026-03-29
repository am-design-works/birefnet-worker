# BiRefNet Background Removal Worker for RunPod Serverless
# Lightweight GPU worker for high-quality background removal

FROM python:3.11-slim

LABEL maintainer="Amoeba Works"
LABEL description="BiRefNet background removal serverless worker"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Pre-download models to avoid cold-start download
# Using u2net first as it's more reliable
RUN python -c "from rembg import new_session; s = new_session('u2net'); print('u2net loaded')"

# Try birefnet-general (may fail on CPU-only build, that's ok)
RUN python -c "from rembg import new_session; s = new_session('birefnet-general'); print('birefnet loaded')" || \
    echo "BiRefNet pre-download skipped (will download on first GPU use)"

# Copy handler
COPY handler.py /handler.py

# RunPod serverless entry
CMD ["python", "-u", "/handler.py"]
