import os
import pickle
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Define SCOPES - Drive API scope
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Function to authenticate the user
def authenticate():
    creds = None
    # Check if token.pickle exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials, log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Run the OAuth flow using the console (headless method)
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_console()

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

# Function to list files from Google Drive
def list_files():
    creds = authenticate()

    # Build the service
    service = build('drive', 'v3', credentials=creds)

    # List files in the Google Drive root folder
    results = service.files().list(
        pageSize=10, fields="files(id, name)").execute()

    # Get the files
    items = results.get('files', [])

    if not items:
        st.write('No files found.')
    else:
        st.write('Files:')
        for item in items:
            st.write(f'{item["name"]} (ID: {item["id"]})')

# Streamlit Frontend
st.title("Google Drive File Listing")

# Display the files from Google Drive
list_files()
