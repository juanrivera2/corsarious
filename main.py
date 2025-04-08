from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import shutil
import os
import tempfile
import requests

# Runpod URL for API call to trigger the workflow
RUNPOD_URL = "https://api.runpod.ai/v2/f2hkgd82l435k0/run"

# Function to call the Runpod API and execute the workflow
def execute_runpod_workflow(file_path):
    headers = {
        "Content-Type": "application/json",
        # Add any necessary headers like API key if required
    }
    payload = {
        "file": file_path,
        # Include other parameters required by the Runpod API
    }
    response = requests.post(RUNPOD_URL, json=payload, headers=headers)
    return response.json()

# 🔗 Import your processing logic
from test_converting_a_checklist import process_image_and_extract_tables, generate_audio_from_text

# Initialize FastAPI app
app = FastAPI()

# Create a static temp directory to serve files
TEMP_DIR = os.path.join(tempfile.gettempdir(), "checklist_temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# Mount static file directory so /temp/audio.mp3 can be accessed via HTTP
app.mount("/temp", StaticFiles(directory=TEMP_DIR), name="temp")


@app.post("/process")
def process_file(file: UploadFile = File(...)):
    try:
        # 1. Save uploaded image to temp folder
        temp_image_path = os.path.join(TEMP_DIR, file.filename)
        with open(temp_image_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # 2. Execute the workflow with Runpod (send the file to Runpod for GPU processing)
        runpod_response = execute_runpod_workflow(temp_image_path)

        # Check for Runpod response errors
        if "error" in runpod_response:
            return JSONResponse(status_code=500, content={"status": "error", "message": runpod_response["error"]})

        # 3. Open image using PIL and process it
        image = Image.open(temp_image_path)

        # 4. 🔍 Process image and extract tables
        detected_tables = process_image_and_extract_tables(image)

        if not detected_tables:
            return JSONResponse(status_code=404, content={"status": "warning", "message": "No tables detected."})

        # 5. 🎧 Generate MP3 from detected tables
        mp3_filename = f"{os.path.splitext(file.filename)[0]}_extracted_tables.mp3"
        mp3_path = os.path.join(TEMP_DIR, mp3_filename)
        generate_audio_from_text(detected_tables, mp3_path)

        # 6. Return path to audio file
        return JSONResponse(status_code=200, content={
            "status": "success",
            "audio_url": f"/temp/{mp3_filename}"
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
