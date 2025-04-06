# streamlit_ui/app.py

import streamlit as st
import requests

API_URL = "https://corsarious-production.up.railway.app/"  # Replace with actual Railway FastAPI URL

st.set_page_config(page_title="Checklist Pipeline", layout="centered")
st.title("Checklist AI Pipeline")

if st.button("Run Checklist Conversion"):
    with st.spinner("Running pipeline..."):
        try:
            response = requests.get(f"{API_URL}/run-checklist-conversion")
            if response.ok:
                data = response.json()
                st.success("Pipeline completed successfully!" if data["status"] == "success" else "Pipeline finished with errors.")
                
                st.subheader("Console Output")
                st.code(data.get("stdout", ""), language="bash")

                if data.get("stderr"):
                    st.subheader("Errors")
                    st.error(data["stderr"])
            else:
                st.error("Failed to reach FastAPI endpoint.")
        except Exception as e:
            st.error(f"Error: {str(e)}")