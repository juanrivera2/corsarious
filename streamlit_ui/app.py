import streamlit as st
import requests

# FastAPI URL
API_URL = "https://corsarious-production.up.railway.app/"  # Replace with the actual FastAPI URL

# Streamlit UI Setup
st.set_page_config(page_title="Checklist AI Pipeline", layout="centered")
st.title("Checklist AI Pipeline")

# File Upload Section
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

# Process the image when uploaded
if uploaded_file is not None:
    st.write("Processing your file...")

    try:
        # Send the uploaded file to FastAPI for processing
        files = {'file': uploaded_file.getvalue()}
        response = requests.post(f"{API_URL}/process", files=files)

        if response.status_code == 200:
            result = response.json()
            st.success(f"MP3 file generated successfully!")
            st.audio(result['audio_url'])  # Play the generated MP3 file
        else:
            st.error(f"Error: {response.json()['message']}")

    except Exception as e:
        st.error(f"Error: {str(e)}")
