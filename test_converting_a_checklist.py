import os
import cv2
import numpy as np
from PIL import Image
import easyocr
from gtts import gTTS
from pydub import AudioSegment
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil

reader = get_reader()
table_text = reader.readtext(roi)
app = FastAPI()

def get_reader():
    return easyocr.Reader(['en'])

    reader = get_reader()
    table_text = reader.readtext(roi)

# Function to process image and detect tables
def process_image_and_extract_tables(image):
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    dilated = cv2.dilate(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected_tables = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 100 and h > 50:
            roi = img[y:y + h, x:x + w]
            table_text = reader.readtext(roi)

            if table_text:
                detected_text = " ".join([text[1] for text in table_text])
                detected_text = normalize_text(detected_text)
                detected_tables.append(detected_text)

    return detected_tables

# Normalize detected text for consistency
def normalize_text(text):
    text = text.replace("\n", " ")
    text = text.strip()
    text = text.lower()
    text = text.capitalize()
    return text

# Generate MP3 from extracted tables
def generate_audio_from_text(table_texts, output_filename):
    combined_audio = AudioSegment.silent(duration=1000)

    for table_text in table_texts:
        rows = table_text.split(".")

        for row in rows:
            row = row.strip()
            if row:
                tts = gTTS(text=row, lang='en')
                temp_file = tempfile.NamedTemporaryFile(delete=True, suffix=".mp3")
                tts.save(temp_file.name)
                audio_segment = AudioSegment.from_mp3(temp_file.name)
                combined_audio += audio_segment
                combined_audio += AudioSegment.silent(duration=5000)

        tts_section = gTTS(text="SECTION IS COMPLETED", lang='en')
        temp_section_file = tempfile.NamedTemporaryFile(delete=True, suffix=".mp3")
        tts_section.save(temp_section_file.name)
        section_completed_audio = AudioSegment.from_mp3(temp_section_file.name)
        combined_audio += section_completed_audio
        combined_audio += AudioSegment.silent(duration=10000)

    combined_audio.export(output_filename, format="mp3")

# FastAPI route to process file upload
@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        temp_path = f"temp/{file.filename}"
        os.makedirs("temp", exist_ok=True)
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Process image and detect tables
        detected_tables = []
        image = Image.open(temp_path)
        detected_tables = process_image_and_extract_tables(image)

        if not detected_tables:
            return JSONResponse(status_code=404, content={"status": "warning", "message": "No tables detected."})

        # Generate audio from detected tables
        temp_dir = tempfile.gettempdir()
        mp3_filename = os.path.join(temp_dir, f"{file.filename}_extracted_tables.mp3")
        generate_audio_from_text(detected_tables, mp3_filename)

        return JSONResponse(status_code=200, content={"status": "success", "audio_url": mp3_filename})

    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
