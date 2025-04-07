from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import shutil
import os

# 🔗 Import the real logic from the renamed file
from test_converting_a_checklist import process_image_and_extract_tables, generate_audio_from_text

# Init FastAPI app
app = FastAPI()

# Make sure temp directory exists
os.makedirs("temp", exist_ok=True)

# Mount static file directory so /temp/audio.mp3 can be accessed via HTTP
app.mount("/temp", StaticFiles(directory="temp"), name="temp")


@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    try:
        # 1. Save uploaded image to temp folder
        temp_path = f"temp/{file.filename}"
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # 2. Open image using PIL
        image = Image.open(temp_path)

        # 3. 🔍 Run the real processing logic
        detected_tables = process_image_and_extract_tables(image)

        if not detected_tables:
            return JSONResponse(status_code=404, content={"status": "warning", "message": "No tables detected."})

        # 4. 🎧 Generate MP3
        mp3_filename = f"{file.filename}_extracted_tables.mp3"
        mp3_path = os.path.join("temp", mp3_filename)
        generate_audio_from_text(detected_tables, mp3_path)

        # 5. Return path to audio file
        return JSONResponse(status_code=200, content={
            "status": "success",
            "audio_url": f"temp/{mp3_filename}"
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
