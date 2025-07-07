import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from transformers import CLIPTokenizer
from PIL import Image
from io import BytesIO
import torch
import base64
import os
import mysql.connector
from datetime import datetime
from backend.sd.pipeline import generate
from backend.sd import model_loader
import random
import numpy as np  
import json
from collections import deque
from contextlib import asynccontextmanager
from time import time   
import sys
from pathlib import Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

MAX_QUEUE_SIZE = 5
processing_queue = deque()
queue_lock = asyncio.Lock()
job_progress = {}  # queue_id -> {percent, eta, time_taken}
job_cancel_flags = {}  # queue_id -> True if cancel requested

os.makedirs("saved_images", exist_ok=True)

base_path = Path(__file__).resolve().parent
ip_path = base_path / "ip.json"
vocab_path = base_path / "data" / "vocab.json"
merges_path = base_path / "data" / "merges.txt"

def create_tables():
    db = get_db()
    cursor = db.cursor()

    # USERS table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255),
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role ENUM('user','admin') DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # IMAGES_GENERATED table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images_generated (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            prompt TEXT NOT NULL,
            image_url TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # GENERATION_QUEUE table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generation_queue (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            prompt TEXT,
            negative_prompt TEXT,
            input_image LONGBLOB,
            status ENUM('queued','processing','done','failed') DEFAULT 'queued',
            result_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)

    # Add default admin if not exists
    admin_email = "jatin123@gmail.com"

    cursor.execute("SELECT * FROM users WHERE email = %s", (admin_email,))
    if cursor.fetchone() is None:
        cursor.execute("""
            INSERT INTO users (username, email, password, role)
            VALUES (%s, %s, %s, %s)
        """, (
            "admin",
            admin_email,
            "jatin123",  # Consider hashing this
            "admin"
        ))


    db.commit()
    cursor.close()
    db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables() 
    asyncio.create_task(process_queue())  # Only one worker to ensure sequential generation
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/saved_images", StaticFiles(directory="saved_images"), name="saved_images")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

DEVICE = "cpu"
print(f"Using device: {DEVICE}")

with open(ip_path, "r") as f:
    backendURL = json.load(f)["ip"]
    
print("Loading vocab from:", vocab_path)

tokenizer = CLIPTokenizer(
    str(vocab_path),
    merges_file=merges_path
)

model_file = base_path / "data" / "v1-5-pruned-emaonly.ckpt"
models = model_loader.preload_models_from_standard_weights(model_file, DEVICE)

def get_db():
    import time
    max_retries = 5
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            return mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", 3306)),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "stable")
            )
        except mysql.connector.Error as e:
            print(f"MySQL connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    email: str
    password: str

def base64_to_image(base64_str):
    try:
        if base64_str.startswith("data:image"):
            base64_str = base64_str.split(",", 1)[1]
        return Image.open(BytesIO(base64.b64decode(base64_str))).convert("RGB")
    except Exception as e:
        print("[Image Decode Error]", e)
        return None

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.post("/register")
def register_user(user: UserRegister):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
            (user.username, user.email, user.password, user.role)
        )
        db.commit()
        user_id = cursor.lastrowid  
        return {
            "message": "User registered successfully",
            "user_id": user_id       
        }
    except mysql.connector.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    finally:
        cursor.close()
        db.close()


@app.post("/login")
def login(user: UserLogin):
    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)

    cursor.execute("SELECT id, role FROM users WHERE (email = %s OR username = %s) AND password = %s",
                   (user.email, user.email, user.password))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    if result:
        return {"user_id": result["id"], "role": result["role"]}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/user-info/{user_id}")
def get_user_info(user_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT username, email, created_at,
        (SELECT COUNT(*) FROM images_generated WHERE user_id = %s) AS total_images
        FROM users WHERE id = %s
    """, (user_id, user_id))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    if result:
        return result
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/user-images/{user_id}")
def get_user_images(user_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, prompt, image_url, timestamp
        FROM images_generated
        WHERE user_id=%s
        ORDER BY timestamp DESC
    """, (user_id,))
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return results

from fastapi import status

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    db = get_db()
    cursor = db.cursor()
    try:
        # Delete images generated by user
        cursor.execute("DELETE FROM images_generated WHERE user_id = %s", (user_id,))
        # Delete generation queue entries (optional, if you want to clear pending tasks)
        cursor.execute("DELETE FROM generation_queue WHERE user_id = %s", (user_id,))
        # Delete user
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()
        return {"detail": "User and related images deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")
    finally:
        cursor.close()
        db.close()

@app.delete("/images/{image_id}")
def delete_image(image_id: int):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM images_generated WHERE id = %s", (image_id,))
        db.commit()
        return {"detail": "Image deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")
    finally:
        cursor.close()
        db.close()
        
@app.get("/users")
def get_all_users():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email, role, created_at FROM users")
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return users


@app.get("/user-queue/{user_id}")
def get_user_queue(user_id: int):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, prompt, status, result_url as image_url, updated_at as timestamp FROM generation_queue WHERE user_id=%s ORDER BY updated_at DESC", (user_id,))
    results = cursor.fetchall()
    cursor.close()
    db.close()
    return results

@app.get("/progress/{queue_id}")
async def get_progress(queue_id: int):
    return job_progress.get(queue_id, {"percent": 100, "eta": 0, "time_taken": 0})

@app.post("/cancel/{queue_id}")
async def cancel_generation(queue_id: int):
    job_cancel_flags[queue_id] = True
    return {"message": f"Cancellation requested for {queue_id}"}

from fastapi import Depends

@app.delete("/clear-queue/{user_id}")
def clear_queue(user_id: int):
    db = get_db()
    cursor = db.cursor()
    try:
        # Delete all queue items for the user
        cursor.execute("DELETE FROM generation_queue WHERE user_id = %s", (user_id,))
        db.commit()
        return {"detail": "All queue items cleared"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear queue: {str(e)}")
    finally:
        cursor.close()
        db.close()



@app.post("/queue")
async def enqueue_generation(request: Request):
    
    payload = await request.json()
    prompt = payload.get("prompt", "").strip()
    negative_prompt = payload.get("uncond_prompt", "").strip()
    input_image = payload.get("input_image")
    user_id = payload.get("user_id")

    if not prompt or not user_id:
        raise HTTPException(status_code=400, detail="Prompt and user_id are required")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO generation_queue (user_id, prompt, negative_prompt, input_image) VALUES (%s, %s, %s, %s)",
                   (user_id, prompt, negative_prompt, input_image))
    db.commit()
    queue_id = cursor.lastrowid
    cursor.close()
    db.close()

    async with queue_lock:
        if len(processing_queue) >= MAX_QUEUE_SIZE:
            return {"message": "Queue is full. Please wait and try again.", "queue_full": True}
        processing_queue.append({"queue_id": queue_id, "user_id": user_id, "prompt": prompt, "negative_prompt": negative_prompt, "input_image": input_image})

    return {"message": "Prompt added to queue successfully.", "queue_id": queue_id}

async def process_queue():
    while True:
        job = None
        async with queue_lock:
            if processing_queue:
                job = processing_queue.popleft()

        if not job:
            await asyncio.sleep(0.5)
            continue

        queue_id = job["queue_id"]
        start_time = time()
        job_progress[queue_id] = {"percent": 0, "eta": None, "time_taken": 0}

        def progress_callback(step, total):
            elapsed = time() - start_time
            percent = int((step / total) * 100)
            eta = (elapsed / step * (total - step)) if step > 0 else None
            job_progress[queue_id].update({"percent": percent, "eta": round(eta, 2) if eta else None})

        

        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("UPDATE generation_queue SET status='processing' WHERE id=%s", (queue_id,))
            db.commit()

            input_image = base64_to_image(job["input_image"]) if job["input_image"] else None
            if input_image:
                n_inference_steps=100
            else:
                n_inference_steps=60

            output_image = await asyncio.to_thread(
                generate,
                prompt=job["prompt"],
                uncond_prompt=job["negative_prompt"],
                input_image=input_image,
                strength=0.6 if input_image else 1,
                do_cfg=True,
                cfg_scale=10,
                sampler_name="ddpm",
                n_inference_steps=n_inference_steps,
                # seed=random.randint(0, 2**10),
                seed=42,
                models=models,
                device=DEVICE,  
                idle_device=DEVICE,
                tokenizer=tokenizer,
                callback=progress_callback,
                cancel_flag=lambda: job_cancel_flags.get(queue_id, False)
            )

            total_time = round(time() - start_time, 2)
            job_progress[queue_id]["time_taken"] = total_time

            if output_image is None:
                cursor.execute("UPDATE generation_queue SET status='cancelled' WHERE id=%s", (queue_id,))
                db.commit()
                continue

            if isinstance(output_image, torch.Tensor):
                output_image = output_image.detach().cpu().numpy()

            img = Image.fromarray(output_image.astype(np.uint8))
            filename = f"queue_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
            path = os.path.join("saved_images", filename)
            img.save(path)

            cursor.execute("UPDATE generation_queue SET status='done', result_url=%s WHERE id=%s", (filename, queue_id))
            cursor.execute("INSERT INTO images_generated (user_id, prompt, image_url) VALUES (%s, %s, %s)", (job["user_id"], job["prompt"], filename))

            db.commit()

        except Exception as e:
            print("[ERROR] Job failed:", e)
            cursor.execute("UPDATE generation_queue SET status='failed' WHERE id=%s", (queue_id,))
            db.commit()
        finally:
            cursor.close()
            db.close()
            job_progress.pop(queue_id, None)
            job_cancel_flags.pop(queue_id, None)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        access_log=False,
        log_level="info",
    )
