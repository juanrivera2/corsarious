# -*- coding: utf-8 -*-
"""7(6)_Partial_completion_of_checklists.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1KYwEPNN83R3Wl388Ai1dS2YkpAyu-ALo
"""

from pymongo import MongoClient

# MongoDB connection setup (do it once at the start)
client = MongoClient('mongodb://localhost:27017/')
db = client['your_database_name']
scripts_collection = db['Scripts']  # The collection where MP3s and transcriptions will be stored

# Function to upload MP3 file info to MongoDB
def upload_mp3_to_mongo(mp3_file_path):
    filename = os.path.basename(mp3_file_path)

    checklist_name, version, date_str, time_str = extract_date_time_version_from_filename(filename)

    if checklist_name and version and date_str and time_str:
        # Prepare data to be stored in MongoDB
        observation_data = {
            "filename": filename,
            "checklist_name": checklist_name,  # Name of the checklist
            "file_date": date_str,  # Extracted date
            "file_time": time_str,  # Extracted time
            "version": version,     # Version of the checklist
            "mp3_file_path": mp3_file_path  # Path to MP3 file
        }

        # Insert observation data into MongoDB
        scripts_collection.insert_one(observation_data)
        print(f"MP3 {filename} uploaded to MongoDB with version {version} on date {date_str}")

# Function to get all MP3 files for a specific checklist on the same date
def get_mp3_files_for_checklist_on_date(folder_path, checklist_name, date_str):
    mp3_files = []

    # List all files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.mp3'):
            # Extract the details from the filename
            checklist, version, date, time = extract_date_time_version_from_filename(file_name)

            # Filter by checklist name and date
            if checklist == checklist_name and date == date_str:
                mp3_files.append(os.path.join(folder_path, file_name))

    # Sort the files by version
    mp3_files.sort(key=lambda x: extract_date_time_version_from_filename(os.path.basename(x))[1])  # Sort by version
    return mp3_files

# Function to process and combine MP3 files for a specific checklist on the same date
def process_and_combine_mp3_files(folder_path, checklist_name, date_str):
    # Get the list of MP3 files for the checklist on that date
    mp3_files = get_mp3_files_for_checklist_on_date(folder_path, checklist_name, date_str)

    if not mp3_files:
        print(f"No MP3 files found for checklist {checklist_name} on date {date_str}")
        return

    # Combine the MP3s into a single final transcription (for simplicity, we just combine text here)
    combined_transcription = ""

    for mp3_file in mp3_files:
        # Here we would process the MP3 and get a transcription (you can use any speech-to-text library)
        # For simplicity, let's assume we just append the filename as a "dummy transcription"
        combined_transcription += f"Transcription from {mp3_file}\n"

    # Now store the final transcription in MongoDB
    final_transcription_data = {
        "checklist_name": checklist_name,
        "file_date": date_str,
        "final_transcription": combined_transcription
    }

    # Insert the final transcription data into MongoDB
    db['FinalTranscriptions'].insert_one(final_transcription_data)
    print(f"Final transcription for {checklist_name} on {date_str} saved to MongoDB.")

# Example usage
folder_path = '/path/to/AIVoiceobservations/'

# Get the list of checklists
checklist_name = "observation"  # Example checklist name
date_str = "2023-04-04"  # Example date

# Process and combine MP3 files for this checklist and date
process_and_combine_mp3_files(folder_path, checklist_name, date_str)