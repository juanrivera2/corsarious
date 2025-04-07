from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
import tempfile
import io
from gtts import gTTS

app = FastAPI()

@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    try:
        # 1. Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        with open(temp_file.name, "wb") as f:
            f.write(await file.read())

        # 2. Replace this with actual OCR logic (easyocr, cv2, etc.)
        extracted_text = "This is a placeholder checklist text extracted from the image."

        # 3. Convert text to speech using gTTS
        tts = gTTS(extracted_text)
        mp3_io = io.BytesIO()
        tts.write_to_fp(mp3_io)
        mp3_io.seek(0)

        # 4. Stream the audio back
        return StreamingResponse(mp3_io, media_type="audio/mpeg")

    except Exception as e:
        return JSONResponse(content={"message": f"An error occurred: {str(e)}"}, status_code=500)
