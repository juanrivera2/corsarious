import os
import re
import pickle
import pandas as pd
import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import shutil

# Google API Scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER_NAME = 'AIVoiceobservations'

@st.cache_resource
def authenticate():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=8501)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def get_folder_id(service, folder_name):
    response = service.files().list(
        q=f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    folders = response.get('files', [])
    return folders[0]['id'] if folders else None

def list_files_in_folder(service, folder_id):
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        spaces='drive',
        fields='files(id, name)'
    ).execute()
    return results.get('files', [])

def extract_file_metadata(file_list):
    data = []
    pattern = r"([a-zA-Z_]+)_(\d+)_(\d{4}-\d{2}-\d{2})_(\d{2}\.\d{2})"

    for file in file_list:
        filename = file["name"]
        match = re.match(pattern, filename)
        if match:
            data.append({
                "filename": filename,
                "name": match.group(1),
                "version": int(match.group(2)),
                "date": match.group(3),
                "time": match.group(4)
            })
    return pd.DataFrame(data)

def unify_files_by_name_date(df):
    """ Group files by name and date, then sort by version within each group. """
    grouped = df.groupby(['name', 'date'])
    unified_files = {}
    
    for (name, date), group in grouped:
        sorted_group = group.sort_values(by=["version"]).reset_index(drop=True)
        unified_files[(name, date)] = sorted_group["filename"].tolist()
    
    return unified_files

# ---------- Streamlit UI ----------
st.set_page_config(page_title="📁 Voice File Viewer", layout="wide")
st.title("🎙️ AI Voice Observations - File Explorer")

with st.spinner("🔐 Authenticating..."):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

folder_id = get_folder_id(service, FOLDER_NAME)
if not folder_id:
    st.error(f"Folder '{FOLDER_NAME}' not found in Google Drive.")
    st.stop()

files = list_files_in_folder(service, folder_id)

# Extract metadata and show table
df = extract_file_metadata(files)
df = df.sort_values(by=["name", "date", "version"]).reset_index(drop=True)

# Group and unify files by name and date
unified_files = unify_files_by_name_date(df)

# Display the unified files to be processed
st.subheader("🗂️ Unified Files by Name & Date")
for (name, date), files in unified_files.items():
    st.write(f"**Name**: {name}, **Date**: {date}")
    for file in files:
        st.write(f"- {file}")

# Return the unified files for downstream processing
# This will be a list of files ready for denoising/transcription
unified_files  # This can be used in the next step for denoising/transcription
