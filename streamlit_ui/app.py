import streamlit as st
import requests

API_URL = "https://corsarious-production.up.railway.app"  # Replace with your FastAPI URL

st.set_page_config(page_title="Checklist Pipeline", layout="centered")
st.title("Checklist AI Pipeline")

uploaded_file = st.file_uploader("Upload Checklist Image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    st.info("Processing image...")
    try:
        files = {"file": ("filename.png", uploaded_file.getvalue(), uploaded_file.type)}
        response = requests.post(f"{API_URL}/process", files=files)

        if response.status_code == 200:
            st.success("MP3 file generated successfully!")
            st.audio(response.content, format="audio/mp3")
        else:
            # Try to extract error message if it's JSON
            try:
                error_message = response.json().get("message", "Unknown error occurred.")
            except Exception:
                error_message = "Non-JSON error response received."

            st.error(f"API Error: {error_message}")
    except Exception as e:
        st.error(f"Client Error: {str(e)}")
