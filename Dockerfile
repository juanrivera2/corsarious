# Use CUDA-enabled PyTorch image from RunPod
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# Avoid Python output buffering
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# System packages for EasyOCR, ffmpeg, OpenCV
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy all files into the container
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Confirm CUDA is available (for logs/debugging)
RUN python -c "import torch; print('✅ CUDA available:', torch.cuda.is_available())"

# Expose port for FastAPI
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
