# BiRefNet Background Removal Worker for RunPod Serverless
# Lightweight GPU worker for high-quality background removal
#
# Deploy: RunPod Serverless → Custom Source → Build from GitHub
# GPU: RTX 3090 / RTX 4000 Ada / A4000 (16GB+ VRAM recommended)

FROM runpod/base:0.6.2-cuda12.2.0

LABEL maintainer="Amoeba Works"
LABEL description="BiRefNet background removal serverless worker"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Pre-download BiRefNet model (avoids cold-start download)
# This downloads to ~/.u2net/BiRefNet-general-epoch_244.onnx (~970MB)
RUN python -c "from rembg import new_session; new_session('birefnet-general')" && \
    echo "BiRefNet model downloaded successfully"

# Also pre-download u2net as fallback
RUN python -c "from rembg import new_session; new_session('u2net')" && \
    echo "U2Net model downloaded successfully"

# Copy handler
COPY handler.py /handler.py

# RunPod serverless entry
CMD ["python", "-u", "/handler.py"]
