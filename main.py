from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
import subprocess  # <--- This was missing

app = FastAPI()

# Allow frontend to connect (CORS settings)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Later: restrict to your Streamlit app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    try:
        os.makedirs("temp", exist_ok=True)
        temp_path = f"temp/{file.filename}"

        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Run your script and pass temp_path as argument (optional if your script uses fixed input)
        result = subprocess.run(
            ["python", "1_test_converting_a_checklist.py", temp_path],
            capture_output=True,
            text=True
        )

        # Log output or return result.stdout if needed
        extracted_text = result.stdout or f"✅ Mock processed text from: {file.filename}"
        audio_url = "https://example.com/audio.mp3"  # Placeholder

        return JSONResponse(
            content={"status": "success", "text": extracted_text, "audio_url": audio_url}
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )