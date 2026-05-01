# ── NeuroFusion Inference Server ─────────────────────────────────────────────
# This runs ON HuggingFace Spaces as the model inference server.
# The AWS FastAPI backend calls this API to generate images.
# 
# HF Space URL will be: https://jatinnath-neurofusion.hf.space
# 
# Deploy steps:
#   git clone https://huggingface.co/spaces/Jatinnath/neurofusion
#   cp -r hf_space/* .  (inside cloned space repo)
#   git lfs track "*.ckpt"
#   git add . && git commit -m "deploy" && git push

FROM python:3.11-slim

# OS deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# SD model code
COPY sd/ ./sd/

# Tokenizer data files (vocab.json, merges.txt)
COPY data/ ./data/

# Model weights — committed to this Space repo via git-lfs
# File: data/v1-5-pruned-emaonly.ckpt  (~4 GB, tracked with git-lfs)

COPY app.py .

# HuggingFace Spaces expects the app on port 7860
EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
