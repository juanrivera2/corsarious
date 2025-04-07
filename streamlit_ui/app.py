import streamlit as st
import requests
from io import BytesIO

# Updated with your hosted API URL
API_URL = "https://corsarious-production.up.railway.app/process"
BASE_FILE_URL = "https://corsarious-production.up.railway.app"

st.title("Checklist AI Pipeline")

uploaded_file = st.file_uploader("Upload Checklist Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.write("Processing your checklist...")

    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}

    with st.spinner("Running checklist conversion..."):
        response = requests.post(API_URL, files=files)

        if response.status_code == 200:
            data = response.json()
            audio_path = data.get("audio_url")

            if audio_path:
                # Full URL to fetch the audio file
                audio_url = f"{BASE_FILE_URL}/{audio_path}"

                # Fetch the audio file content
                audio_response = requests.get(audio_url)

                if audio_response.status_code == 200:
                    st.success("MP3 file generated successfully!")
                    st.audio(BytesIO(audio_response.content), format="audio/mp3")
                    st.download_button(
                        label="Download MP3",
                        data=audio_response.content,
                        file_name="checklist_audio.mp3",
                        mime="audio/mpeg"
                    )
                else:
                    st.error("Failed to fetch the MP3 file.")
            else:
                st.warning("No audio path was returned from the backend.")
        else:
            try:
                error_message = response.json().get("message")
                st.error(f"Backend error: {error_message}")
            except:
                st.error("An unknown error occurred.")
