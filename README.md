# NeuroFusion — AI Image Generator

> A full-stack mobile and web application that brings **Stable Diffusion** image generation to your pocket. Built with **React Native (Expo)** on the frontend and **FastAPI** on the backend, NeuroFusion lets users generate stunning AI images from text prompts, enhance existing images with img2img, track generation progress in real-time, and manage their personal gallery — all from a sleek, dark-themed interface.

## Example Generations

<img src="https://github.com/user-attachments/assets/2e664f49-05cb-4172-b9db-70ffc4fe66d6" width="300"/>
<img src="https://github.com/user-attachments/assets/0339625d-03d0-404d-88dd-bc9b2415ef08" width="300"/>
<img src="https://github.com/user-attachments/assets/f594154f-392d-4d43-ac78-f283a5302f59" width="300"/>
<img src="https://github.com/user-attachments/assets/e4f48635-e39e-4bfd-9c3d-4642794b3c49" width="300"/>
<img src="https://github.com/user-attachments/assets/b56904ef-b78c-46e6-855e-c541019a423a" width="300"/>
<img src="https://github.com/user-attachments/assets/a680e117-b572-4b19-a17b-06da2ca6a1d0" width="300"/>
<img width="900" src="https://github.com/user-attachments/assets/5b7fffe6-47e3-4b24-a23a-c5a38b8df95a" />
<img width="900" alt="Image" src="https://github.com/user-attachments/assets/b7680916-0848-4502-ac47-cedf00a3a1a5" />
<img width="900"  src="https://github.com/user-attachments/assets/b5cce8cc-3c11-4706-a430-b184105a85de" />
<br/><br/>

### Hyperparameter Comparison

Below are example outputs generated using the same prompt. Differences in images arise due to changes in hyperparameters such as CFG scale, inference steps, and seed.

<img width="1204" height="621" alt="Hyperparameter comparison 1" src="https://github.com/user-attachments/assets/cb166f56-7206-4609-b21d-8ea10f5b8b96" />

<img width="1199" height="612" alt="Hyperparameter comparison 2" src="https://github.com/user-attachments/assets/5c3ba0b9-5ddc-45d0-8b79-42e2beb60211" />

---

## App Overview and Working

- [Watch Web Demo (Download/View)](https://github.com/user-attachments/assets/4dfeb53a-b648-4bef-9265-82cfb9ad1df7)
- [Watch Mobile Demo (Download/View)](https://github.com/user-attachments/assets/e8cfd03a-a0ef-413e-98a9-2ec217bc2880)

---

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [AI Pipeline: Stable Diffusion Deep Dive](#ai-pipeline-stable-diffusion-deep-dive)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Screens & Features](#screens--features)
- [Example Generations](#example-generations)
- [App Overview and Working](#app-overview-and-working)
- [Tech Stack](#tech-stack)
- [Environment Variables](#environment-variables)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Development (Manual)](#local-development-manual)
  - [Docker Deployment](#docker-deployment)
- [Configuration](#configuration)
- [Queue System](#queue-system)
- [Admin Dashboard](#admin-dashboard)
- [Known Limitations](#known-limitations)
- [Reference Papers](#reference-papers)
- [License](#license)

---

## Overview

NeuroFusion is an end-to-end AI image generation platform built on top of a **from-scratch implementation of Stable Diffusion v1.5**. Unlike wrappers around HuggingFace's `diffusers`, the SD pipeline here is implemented component-by-component — CLIP encoder, VAE encoder/decoder, UNet diffusion model, and the DDPM sampler — giving full control over the inference loop, including custom cancellation callbacks and per-step progress reporting.

Built with **Expo** for seamless deployment across Android, iOS, and Web, and a **FastAPI** backend for image processing, queueing, and cancellation logic. Integrated **CLIP Tokenizer** with a custom **UNet-based Diffusion Model** for high-quality generation.

---

## Features

- **Text-to-Image** — Generate AI art from any written prompt using a custom Stable Diffusion pipeline.
- **Image-to-Image (img2img)** — Upload a reference image and transform or enhance it with new prompts or styles.
- **Async Queue System** — Requests are queued and processed one-at-a-time to avoid GPU/CPU contention, with a max queue depth of 5.
- **Real-time Progress** — Live diffusion step progress (percentage + ETA) streamed to the client via polling.
- **Cancel Generation** — Cancel pending or in-progress image generation tasks mid-diffusion from your queue.
- **Personal Gallery** — Every completed image is saved and accessible per-user.
- **Admin Dashboard** — Full user and image management for admins.
- **Cross-platform** — Runs on Android, iOS, and Web via Expo.
- **Docker-ready** — One-command deployment with Docker Compose.

---

## System Architecture

```
┌─────────────────┐    HTTP/REST API    ┌─────────────────┐
│   React Native  │◄──────────────────►│   FastAPI       │
│   Frontend      │                     │   Backend       │
│                 │                     │                 │
│ • Navigation    │                     │ • Queue System  │
│ • UI Components │                     │ • AI Pipeline   │
│ • State Mgmt    │                     │ • User Auth     │
└─────────────────┘                     └─────────────────┘
                                                   │
                                                   ▼
                              ┌─────────────────────────────────┐
                              │       Stable Diffusion          │
                              │                                 │
                              │ ┌─────────┐ ┌─────────┐         │
                              │ │  CLIP   │ │   VAE   │         │
                              │ │ Encoder │ │ Encoder │         │
                              │ └─────────┘ └─────────┘         │
                              │           │                     │
                              │     ┌─────▼─────┐               │
                              │     │   UNet    │               │
                              │     │ Diffusion │               │
                              │     └─────┬─────┘               │
                              │           │                     │
                              │     ┌─────▼─────┐               │
                              │     │    VAE    │               │
                              │     │  Decoder  │               │
                              │     └───────────┘               │
                              └─────────────────────────────────┘
                                                   │
                                                   ▼
                                        ┌─────────────────┐
                                        │     MySQL       │
                                        │   Database      │
                                        │                 │
                                        │ • Users         │
                                        │ • Images        │
                                        │ • Queue         │
                                        └─────────────────┘
```

### Component Responsibilities

| Component | Technology | Responsibility |
|-----------|-----------|----------------|
| **Mobile App** | React Native + Expo | UI, navigation, prompt input, gallery, progress polling |
| **API Server** | FastAPI + Uvicorn | REST endpoints, async queue management, auth, file serving |
| **SD Pipeline** | PyTorch (custom) | CLIP encoding → VAE encode → UNet diffusion → VAE decode |
| **Database** | MySQL 8 | Persist users, generated images, and queue state |
| **Static Files** | FastAPI `StaticFiles` | Serve generated PNG images over HTTP |

---

## AI Pipeline: Stable Diffusion Deep Dive

The entire Stable Diffusion v1.5 inference pipeline is implemented from scratch under `backend/sd/`. No `diffusers` library is used — every tensor operation is explicit.

```
Prompt Text
    │
    ▼
┌──────────────────────────────────────────────────────────┐
│  CLIP Tokenizer  (backend/data/vocab.json + merges.txt)  │
│  Converts text → token IDs (max 77 tokens)               │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────┐
│  CLIP Text Encoder  (backend/sd/clip.py)                 │
│  Token IDs → Context Embeddings (768-dim)                │
│  Used for both conditional (prompt) and                  │
│  unconditional (negative prompt) embeddings              │
└───────────────────────┬──────────────────────────────────┘
                        │
          ┌─────────────▼─────────────┐
          │  CFG: Classifier-Free     │
          │  Guidance Scale = 10      │
          │  ε = ε_uncond + scale *   │
          │      (ε_cond - ε_uncond)  │
          └─────────────┬─────────────┘
                        │
┌───────────────────────▼──────────────────────────────────┐
│  VAE Encoder  (backend/sd/encoder.py)  [img2img only]    │
│  Input Image (512×512 RGB)  →  Latent Space (64×64×4)    │
│  Adds noise at strength t ∈ [0,1] (default: 0.6)         │
└───────────────────────┬──────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────┐
│  UNet  (backend/sd/diffusion.py)                         │
│  Iterative denoising via DDPM scheduler                  │
│                                                          │
│  text2img: 60 denoising steps                            │
│  img2img:  100 denoising steps (higher fidelity)         │
│                                                          │
│  At each step:                                           │
│    1. UNet predicts noise residual                       │
│    2. Apply CFG guidance                                 │
│    3. DDPM scheduler removes predicted noise             │
│    4. Progress callback fires → percent + ETA update     │
│    5. Check cancel flag → abort if requested             │
└───────────────────────┬──────────────────────────────────┘
                        │
┌───────────────────────▼──────────────────────────────────┐
│  VAE Decoder  (backend/sd/decoder.py)                    │
│  Denoised Latents (64×64×4) → Pixel Image (512×512 RGB)  │
│  Saves as PNG to ./saved_images/                         │
└──────────────────────────────────────────────────────────┘
```

### SD Module Files

| File | Description |
|------|-------------|
| `backend/sd/pipeline.py` | Main `generate()` function — orchestrates the full inference loop |
| `backend/sd/clip.py` | CLIP text encoder — transforms token embeddings into context vectors |
| `backend/sd/encoder.py` | VAE encoder — encodes pixel images into the 4-channel latent space |
| `backend/sd/decoder.py` | VAE decoder — maps latent vectors back to pixel space |
| `backend/sd/diffusion.py` | UNet architecture — backbone of the denoising process |
| `backend/sd/ddpm.py` | DDPM sampler — manages the noise schedule and step updates |
| `backend/sd/attention.py` | Self-attention and cross-attention layers used by UNet |
| `backend/sd/model_loader.py` | Loads all model weights from the `.ckpt` checkpoint file |
| `backend/sd/model_converter.py` | Converts HuggingFace/CompVis weight keys to match custom architecture |

```



---

## Database Schema

Three tables are auto-created on startup via `create_tables()`:

```sql
-- User accounts
CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(255),
    email       VARCHAR(255) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    role        ENUM('user', 'admin') DEFAULT 'user',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Completed image records
CREATE TABLE images_generated (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT,
    prompt      TEXT NOT NULL,
    image_url   TEXT NOT NULL,          -- filename in saved_images/
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Generation queue (pending, in-progress, done, failed)
CREATE TABLE generation_queue (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    prompt          TEXT,
    negative_prompt TEXT,
    input_image     LONGBLOB,           -- base64-encoded input for img2img
    status          ENUM('queued','processing','done','failed') DEFAULT 'queued',
    result_url      TEXT,               -- filename once generation completes
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**ER Diagram:**

```
┌──────────┐         ┌───────────────────┐        ┌──────────────────┐
│  users   │  1───N  │  images_generated │        │ generation_queue │
│──────────│         │───────────────────│        │──────────────────│
│ id (PK)  │◄────────│ user_id (FK)      │   1──N │ user_id (FK)     │◄──
│ username │         │ prompt            │        │ prompt           │
│ email    │         │ image_url         │        │ negative_prompt  │
│ password │         │ timestamp         │        │ input_image      │
│ role     │         └───────────────────┘        │ status           │
│created_at│◄────────────────────────────────────│ result_url       │
└──────────┘                                      └──────────────────┘
```

---

## API Reference

**Base URL:** `http://<SERVER_IP>:8000`

### Authentication

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| `POST` | `/register` | Register a new user | `{ username, email, password, role? }` |
| `POST` | `/login` | Login with email/username + password | `{ email, password }` |

### User

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/user-info/{user_id}` | Get user profile + total image count |
| `GET` | `/user-images/{user_id}` | List all generated images for a user |
| `GET` | `/users` | List all users (admin) |
| `DELETE` | `/users/{user_id}` | Delete user + all their images and queue entries |

### Image Generation Queue

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| `POST` | `/queue` | Enqueue a new generation job | `{ user_id, prompt, uncond_prompt?, input_image? }` |
| `GET` | `/user-queue/{user_id}` | Get all queue items for a user |
| `GET` | `/progress/{queue_id}` | Get real-time progress `{ percent, eta, time_taken }` |
| `POST` | `/cancel/{queue_id}` | Request cancellation of an active job |
| `DELETE` | `/clear-queue/{user_id}` | Clear all queue entries for a user |

### Images

| Method | Endpoint | Description |
|--------|----------|-------------|
| `DELETE` | `/images/{image_id}` | Delete a generated image record |
| `GET` | `/saved_images/{filename}` | Serve a generated image file (static) |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ping` | Health check — returns `{ "status": "ok" }` |

---

## Project Structure

```
expo_img-v2/
│
├── App.js                          # Root navigator — Stack + Tab navigation
├── index.js                        # Expo entry point
├── app.json                        # Expo project config
├── package.json                    # Node.js dependencies
├── babel.config.js                 # Babel transpiler config
├── tsconfig.json                   # TypeScript config
│
├── screens/                        # React Native screens
│   ├── login.jsx                   # Login screen
│   ├── signup.jsx                  # Registration screen
│   ├── generate.jsx                # Prompt input + img2img upload
│   ├── gallery.jsx                 # Personal image gallery
│   ├── account.jsx                 # User profile & stats
│   ├── MyQueue.jsx                 # Real-time queue monitor & history
│   ├── AdminDashboard.jsx          # Admin: manage users & images
│   └── ip.json                     # Backend IP config (auto-generated)
│
├── assets/                         # Images, fonts, icons
│
├── backend/
│   ├── main.py                     # FastAPI application + all endpoints
│   ├── requirements.txt            # Python dependencies
│   ├── ip.json                     # Backend self-reference IP
│   │
│   ├── sd/                         # Stable Diffusion pipeline (custom PyTorch)
│   │   ├── pipeline.py             # Main generate() orchestrator
│   │   ├── clip.py                 # CLIP text encoder
│   │   ├── encoder.py              # VAE encoder (image → latent)
│   │   ├── decoder.py              # VAE decoder (latent → image)
│   │   ├── diffusion.py            # UNet denoising network
│   │   ├── ddpm.py                 # DDPM noise scheduler
│   │   ├── attention.py            # Self & cross-attention modules
│   │   ├── model_loader.py         # Checkpoint weight loader
│   │   └── model_converter.py      # Weight key conversion utility
│   │
│   └── data/                       # Model data files (not committed)
│       ├── v1-5-pruned-emaonly.ckpt  # SD v1.5 weights (~4 GB)
│       ├── vocab.json              # CLIP tokenizer vocabulary
│       └── merges.txt              # CLIP tokenizer BPE merges
│
├── saved_images/                   # Generated PNG output files
│
├── Dockerfile                      # Docker image build instructions
├── docker-compose.yml              # Local dev: backend + MySQL
├── docker-compose.prod.yml         # Production compose config
├── .dockerignore                   # Docker build exclusions
├── start.sh                        # Container entrypoint (FastAPI + Expo)
├── nginx.conf                      # Nginx reverse proxy config
├── deploy.sh                       # Deployment automation script
│
├── update_ip.py                    # Auto-detect and write host IP to ip.json
└── write_ip.py                     # Manual IP writer utility
```

---

## Screens & Features

### Navigation Flow

```
                    ┌──────────┐
                    │  Login   │
                    └────┬─────┘
            ┌────────────┼────────────┐
            ▼            ▼            ▼
        ┌────────┐  ┌────────┐  ┌─────────┐
        │ Signup │  │  Main  │  │  Admin  │
        └────────┘  │  Tabs  │  │Dashboard│
                    └───┬────┘  └─────────┘
              ┌─────────┼──────────┐
              ▼         ▼          ▼
          ┌────────┐ ┌───────┐ ┌─────────┐
          │Generate│ │Gallery│ │ Account │
          └───┬────┘ └───────┘ └─────────┘
              │
              ▼
          ┌─────────┐
          │ MyQueue │
          └─────────┘
```

### Screen Descriptions

| Screen | File | Key Features |
|--------|------|-------------|
| **Login** | `login.jsx` | Email/password login, admin role redirect, dark glassmorphism UI |
| **Signup** | `signup.jsx` | User registration with validation |
| **Generate** | `generate.jsx` | Prompt + negative prompt input, image picker for img2img, queue submission, "See Progress" link |
| **Gallery** | `gallery.jsx` | Grid view of all user-generated images, tap to enlarge |
| **Account** | `account.jsx` | Username, email, join date, total images generated |
| **My Queue** | `MyQueue.jsx` | Live queue status (QUEUED / PROCESSING / DONE / FAILED / CANCELLED), animated progress bar, ETA countdown, cancel/remove actions, pull-to-refresh, clear all |
| **Admin Dashboard** | `AdminDashboard.jsx` | List all users, drill into any user to see their profile + all generated images, delete users or individual images |

---



## Tech Stack

### Frontend

| Library | Version | Purpose |
|---------|---------|---------|
| React Native | 0.79.4 | Cross-platform mobile framework |
| Expo | 53.0.13 | Toolchain, native module access |
| React Navigation | 7.x | Stack + Tab navigation |
| expo-image-picker | ~16.1.4 | Camera roll access for img2img |
| expo-linear-gradient | ~14.1.5 | UI gradient backgrounds |
| expo-file-system | ^18.1.10 | Local file operations |
| Axios | ^1.10.0 | HTTP client |
| Ionicons | (via Expo) | Icon set |

### Backend

| Library | Version | Purpose |
|---------|---------|---------|
| FastAPI | latest | Async REST API framework |
| Uvicorn | latest | ASGI server |
| PyTorch | 2.5.1 | Deep learning tensor operations |
| Torchvision | 0.20.1 | Image transforms |
| Transformers | 4.33.2 | CLIP tokenizer |
| Pillow | latest | Image I/O and processing |
| mysql-connector-python | latest | MySQL database driver |
| python-dotenv | latest | Environment variable loading |
| aiohttp / aiofiles | latest | Async HTTP + file operations |

### Infrastructure

| Tool | Purpose |
|------|---------|
| MySQL 8 | Primary relational database |
| Docker + Docker Compose | Containerised deployment |
| Nginx | Reverse proxy (production) |
| Expo Tunnel (ngrok) | Expose Expo dev server over the internet |

---

## Environment Variables

Configure these either in a `.env` file or in `docker-compose.yml`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | MySQL host |
| `DB_PORT` | `3306` | MySQL port |
| `DB_USER` | `root` | MySQL username |
| `DB_PASSWORD` | ` ` | MySQL password |
| `DB_NAME` | `stable` | MySQL database name |

In Docker, these are set via the `environment` block in `docker-compose.yml` and automatically point `DB_HOST` to the `mysql` service container.

---

## Getting Started

### Prerequisites

| Requirement | Version |
|------------|---------|
| Python | 3.11+ |
| Node.js | 18+ |
| npm | 9+ |
| MySQL | 8.0+ (or Docker) |
| Expo CLI | latest (`npm install -g expo`) |
| Stable Diffusion Weights | `v1-5-pruned-emaonly.ckpt` (downloaded separately) |

> **Hardware Note:** The SD pipeline runs on CPU by default (`DEVICE = "cpu"`). Generation takes **5–20 minutes per image** on a modern CPU. A CUDA-capable GPU is strongly recommended for production use; simply change `DEVICE = "cuda"` in `backend/main.py`.

---

### Generation Parameters

These are set in the queue processor (`process_queue()` in `main.py`):

| Parameter | text2img | img2img | Description |
|-----------|----------|---------|-------------|
| `n_inference_steps` | 60 | 100 | Number of denoising steps |
| `cfg_scale` | 10 | 10 | Classifier-free guidance strength |
| `strength` | 1.0 | 0.6 | img2img noise strength (0=no change, 1=full generation) |
| `sampler_name` | `ddpm` | `ddpm` | Noise scheduler algorithm |
| `seed` | 42 | 42 | Random seed (fixed for reproducibility) |

### Queue Size

```python
MAX_QUEUE_SIZE = 5   # Maximum pending jobs in memory queue
```

---

## Queue System

The queue is a two-layer system:

```
User submits prompt
        │
        ▼
  ┌─────────────────────────────────┐
  │   MySQL generation_queue table  │  ← Persistent storage (survives restarts)
  │   status: 'queued'              │
  └──────────────┬──────────────────┘
                 │
                 ▼
  ┌─────────────────────────────────┐
  │   In-memory deque (Python)      │  ← Active processing queue (max 5 items)
  │   processing_queue              │
  └──────────────┬──────────────────┘
                 │
                 ▼
  ┌─────────────────────────────────┐
  │   process_queue() async loop    │  ← Single worker, sequential processing
  │   Runs in background task       │
  └──────────────┬──────────────────┘
                 │
         ┌───────┴────────┐
         ▼                ▼
   Job succeeds      Job cancelled/fails
         │                │
  status='done'    status='failed'/'cancelled'
  result_url set
  images_generated row inserted
```

**Why sequential processing?** Stable Diffusion requires significant RAM/VRAM. Running jobs in parallel would cause OOM errors on typical hardware. The single-worker approach ensures each generation gets full resources.

---

## Admin Dashboard

Admins (role = `'admin'`) are redirected to the Admin Dashboard after login instead of the main app.

**Capabilities:**
- **View all users** — list with username, expandable details
- **Drill into any user** — see email, join date, total images, and full image history
- **Delete users** — cascades to delete all their images and queue entries
- **Delete individual images** — removes the record (file cleanup to be implemented)

The default admin account is seeded on first startup:
- Email: `jatin123@gmail.com`
- Password: `jatin123`

> **Warning:** Change the default admin credentials before any production deployment.

---
---

## Reference Papers

- Rombach, R., Blattmann, A., Lorenz, D., Esser, P., & Ommer, B. (2022). [High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/pdf/2112.10752).
- Ho, J., Jain, A., & Abbeel, P. (2020). [Denoising Diffusion Probabilistic Models](https://arxiv.org/pdf/2006.11239).

---

## License

This project is for educational and personal use. The Stable Diffusion v1.5 model weights are subject to the [CreativeML Open RAIL-M License](https://huggingface.co/spaces/CompVis/stable-diffusion-license).

---

<div align="center">
  <strong>Built using React Native, FastAPI, and Stable Diffusion</strong>
</div>
