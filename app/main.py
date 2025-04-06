from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
import gridfs
from datetime import datetime
import subprocess
import os

# FastAPI app
app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# MongoDB setup
client = MongoClient("mongodb+srv://AIDatabase:BTColombia2022@sandbox.bxohv.mongodb.net/?retryWrites=true&w=majority&appName=sandbox")
db = client['AIDatabase']
fs = gridfs.GridFS(db)
reports_collection = db['Reports']

# Directory where the scripts live
SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "scripts")

# List of scripts to run in order
SCRIPTS = [
    "1_test_converting_a_checklist.py",
    "2_convert_word_template.py",
    "3_convert_checklists_to_mp3.py",
    "4_mp3_checklist_questions.py",
    "5_start_stop_answering_process.py",
    "6_partial_completion_of_checklists.py",
    "7_record_date_time_with_mp3_answers.py",
    "8_mp3_checklist_answers_scenarios.py",
    "9_mp3_to_text_and_mongo.py",
    "10_convert_answers_to_word_pdf.py",
    "11_signatures_not_required.py",
    "12_convert_text_to_json_and_transfer.py"
]

def run_pipeline():
    try:
        logs = ""
        for script in SCRIPTS:
            script_path = os.path.join(SCRIPT_DIR, script)
            result = subprocess.run(["python", script_path], capture_output=True, text=True)
            logs += f"\n\n[Running {script}]\n"
            logs += result.stdout
            if result.stderr:
                logs += "\n[Error]\n" + result.stderr
        
        # Save to MongoDB
        file_id = fs.put(logs.encode(), filename=f"Pipeline_Log_{datetime.now().isoformat()}.txt")
        reports_collection.insert_one({
            "date_generated": datetime.now().isoformat(),
            "status": "Completed",
            "log_file_id": file_id,
            "result_type": "Log"
        })

    except Exception as e:
        print(f"Pipeline failed: {e}")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/run-pipeline/")
async def trigger_pipeline(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_pipeline)
    return {"message": "Pipeline started in background."}