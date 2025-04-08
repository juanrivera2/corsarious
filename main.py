from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import shutil
import os
import tempfile
import requests
import torch

# 🔗 Import your local image/audio logic
from test_converting_a_checklist import process_image_and_extract_tables, generate_audio_from_text

# === RunPod Configuration ===
RUNPOD_URL = "https://api.runpod.ai/v2/f2hkgd82l435k0/run"
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")  # Recommended: set in your .env or environment variables

# === Create a temp directory
TEMP_DIR = os.path.join(tempfile.gettempdir(), "checklist_temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# === FastAPI app
app = FastAPI()
app.mount("/temp", StaticFiles(directory=TEMP_DIR), name="temp")

# === RunPod fallback if GPU is not available
def process_with_runpod(image_path):
    with open(image_path, "rb") as img_file:
        files = {
            "file": (os.path.basename(image_path), img_file, "image/jpeg")
        }
        headers = {
            "Authorization": f"Bearer {RUNPOD_API_KEY}"
        }
        response = requests.post(RUNPOD_URL, files=files, headers=headers)

    if response.status_code == 200:
        return response.json().get("output", "")
    else:
        return f"RunPod Error: {response.text}"

# === Core logic switch between local GPU or RunPod
def process_data(image_path):
    if torch.cuda.is_available():
        print("🚀 CUDA available — running locally")
        image = Image.open(image_path)
        return process_image_and_extract_tables(image)
    else:
        print("⚠️ No CUDA — using RunPod")
        return process_with_runpod(image_path)

# === FastAPI Endpoint
@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    try:
        # Save uploaded file to temp path
        temp_image_path = os.path.join(TEMP_DIR, file.filename)
        with open(temp_image_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Process file: Local GPU or RunPod
        extracted_tables = process_data(temp_image_path)

        if not extracted_tables:
            return JSONResponse(status_code=404, content={"status": "warning", "message": "No tables detected."})

        # Generate MP3 from extracted text
        mp3_filename = f"{os.path.splitext(file.filename)[0]}_output.mp3"
        mp3_path = os.path.join(TEMP_DIR, mp3_filename)
        generate_audio_from_text(extracted_tables, mp3_path)

        return JSONResponse(status_code=200, content={
            "status": "success",
            "audio_url": f"/temp/{mp3_filename}"
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
