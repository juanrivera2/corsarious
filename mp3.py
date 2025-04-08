import os
import pickle
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import time

# Authentication scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Function to authenticate
def authenticate():
    creds = None
    # Check if the token.pickle file exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no credentials or they are expired, prompt for authentication
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for future use
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

# Function to list files from Google Drive
def list_drive_files(creds):
    try:
        # Build the Google Drive API client
        service = build('drive', 'v3', credentials=creds)

        # Get a list of files from Google Drive
        results = service.files().list(pageSize=10, fields="files(id, name)").execute()
        files = results.get('files', [])

        # Display files in the app
        if not files:
            st.write("No files found.")
        else:
            st.write("Files in your Google Drive:")
            for file in files:
                st.write(f"{file['name']} (ID: {file['id']})")

    except Exception as e:
        st.write(f"An error occurred: {e}")

# Streamlit UI
def main():
    st.title("Google Drive File Viewer")

    # Show a button to authenticate
    if st.button('Authenticate Google Drive'):
        with st.spinner('Authenticating...'):
            creds = authenticate()
            st.success("Authentication successful!")
        
        # Show files after authentication
        list_drive_files(creds)

if __name__ == '__main__':
    main()
