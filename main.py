from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from gtts import gTTS
import tempfile

app = FastAPI()

@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    try:
        # Save the uploaded image file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        with open(temp_file.name, "wb") as f:
            f.write(await file.read())

        # Assume the image is processed and some text is extracted (you can replace this with OCR processing)
        text = "Sample text extracted from image"  # Replace with actual processing logic (e.g., OCR)

        # Convert the extracted text to speech (MP3)
        tts = gTTS(text)
        audio_path = temp_file.name.replace(".png", ".mp3")
        tts.save(audio_path)

        # Return the path to the generated MP3 file
        return JSONResponse(
            content={"audio_url": audio_path},
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"message": f"An error occurred: {str(e)}"},
            status_code=500
        )
