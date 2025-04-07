from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil
import tempfile
from gtts import gTTS
import os

app = FastAPI()

@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    try:
        # Temporary save the uploaded image
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        with open(temp_file.name, "wb") as f:
            f.write(await file.read())

        # Process the image (e.g., OCR, audio conversion, etc.)
        # For example, if you want to use OCR (easyocr) or generate text-to-speech (gTTS)
        
        # Sample processing - Here we use a basic text-to-speech generation from the image
        # In reality, this part should process the image, extract data, etc.
        text = "Sample extracted text from the image"  # Replace this with your actual processing logic
        
        tts = gTTS(text)
        audio_path = temp_file.name.replace(".png", ".mp3")
        tts.save(audio_path)

        # Return the generated audio file URL or path
        return JSONResponse(
            content={"audio_url": audio_path},  # Here we return the path to the generated MP3
            status_code=200
        )
        
    except Exception as e:
        return JSONResponse(
            content={"message": f"An error occurred: {str(e)}"},
            status_code=500
        )
