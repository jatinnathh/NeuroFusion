"""
NeuroFusion — HuggingFace Space Inference Server
=================================================
Runs ON HuggingFace Spaces. Exposes a single /generate endpoint.
The AWS FastAPI backend calls this to produce images.

Expected file layout inside the Space repo:
  app.py              ← this file
  sd/                 ← copied from backend/sd/
  data/
    vocab.json
    merges.txt
    v1-5-pruned-emaonly.ckpt   ← committed via git-lfs
"""

import base64
import io
import os
import random
from pathlib import Path

import numpy as np
import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from pydantic import BaseModel
from transformers import CLIPTokenizer

from sd import model_loader
from sd.pipeline import generate

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).resolve().parent
DATA_DIR    = BASE_DIR / "data"
VOCAB_PATH  = DATA_DIR / "vocab.json"
MERGES_PATH = DATA_DIR / "merges.txt"
MODEL_FILE  = DATA_DIR / "v1-5-pruned-emaonly.ckpt"

# ── Device ────────────────────────────────────────────────────────────────────
# HF free-tier Spaces are CPU-only.
# Upgrade to a GPU Space ($0.60/hr T4) to change this to "cuda".
DEVICE = os.getenv("DEVICE", "cpu")
print(f"[inference] Using device: {DEVICE}")

# ── Load model once at startup ────────────────────────────────────────────────
print("[inference] Loading tokenizer ...")
tokenizer = CLIPTokenizer(str(VOCAB_PATH), merges_file=str(MERGES_PATH))

print("[inference] Loading SD model weights ...")
models = model_loader.preload_models_from_standard_weights(MODEL_FILE, DEVICE)
print("[inference] Model ready ✓")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="NeuroFusion Inference API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request / Response schemas ────────────────────────────────────────────────
class GenerateRequest(BaseModel):
    prompt:          str
    negative_prompt: str  = ""
    input_image:     str  = None   # base64-encoded image (optional, for img2img)
    strength:        float = 0.6
    cfg_scale:       float = 10.0
    steps:           int   = 60
    seed:            int   = 42


class GenerateResponse(BaseModel):
    image: str   # base64-encoded PNG


# ── Helpers ───────────────────────────────────────────────────────────────────
def _decode_image(b64: str) -> Image.Image:
    if b64.startswith("data:image"):
        b64 = b64.split(",", 1)[1]
    return Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")


def _encode_image(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "device": DEVICE}


@app.post("/generate", response_model=GenerateResponse)
def run_generate(req: GenerateRequest):
    input_image = _decode_image(req.input_image) if req.input_image else None
    n_steps     = req.steps if not input_image else max(req.steps, 100)

    try:
        output = generate(
            prompt           = req.prompt,
            uncond_prompt    = req.negative_prompt,
            input_image      = input_image,
            strength         = req.strength if input_image else 1.0,
            do_cfg           = True,
            cfg_scale        = req.cfg_scale,
            sampler_name     = "ddpm",
            n_inference_steps= n_steps,
            seed             = req.seed,
            models           = models,
            device           = DEVICE,
            idle_device      = DEVICE,
            tokenizer        = tokenizer,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if output is None:
        raise HTTPException(status_code=500, detail="Generation returned None")

    if isinstance(output, torch.Tensor):
        output = output.detach().cpu().numpy()

    img = Image.fromarray(output.astype(np.uint8))
    return GenerateResponse(image=_encode_image(img))
