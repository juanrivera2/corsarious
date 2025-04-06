from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os

app = FastAPI()

# Allow frontend to connect (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    temp_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # TODO: call your existing pipeline logic here with `temp_path`
    # For now, mock result
    extracted_text = f"Mock extracted text from {file.filename}"
    audio_url = "https://example.com/audio.mp3"  # Optional, add if you return audio

    return JSONResponse(content={"text": extracted_text, "audio_url": audio_url})