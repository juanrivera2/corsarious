import os
import pickle
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Authentication scopes
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Function to authenticate
def authenticate():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens.
    # If it exists, we load them and skip the authentication process.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no credentials are available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # If no valid credentials are available, prompt the user to log in.
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)  # Run local server for authentication

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

# Function to list files from Google Drive
def list_drive_files(creds):
    try:
        # Build the Google Drive API client
        service = build('drive', 'v3', credentials=creds)

        # Call the Drive API to list files
        results = service.files().list(pageSize=10, fields="files(id, name)").execute()
        files = results.get('files', [])

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

    # Button to authenticate
    if st.button('Authenticate Google Drive'):
        creds = authenticate()
        st.success("Authentication successful!")

        # Show files after authentication
        list_drive_files(creds)

if __name__ == '__main__':
    main()
