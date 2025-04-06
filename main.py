from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
import gridfs
from datetime import datetime
import papermill as pm
import os

# Initialize FastAPI app
app = FastAPI()

# MongoDB connection
client = MongoClient("mongodb+srv://AIDatabase:BTColombia2022@sandbox.bxohv.mongodb.net/?retryWrites=true&w=majority&appName=sandbox")
db = client['AIDatabase']
fs = gridfs.GridFS(db)
reports_collection = db['Reports']

# Request schema
class RunPipelineRequest(BaseModel):
    milestone: str
    params: dict

# Run notebook with Papermill
def run_notebook(notebook_path: str, output_path: str, parameters: dict):
    pm.execute_notebook(
        notebook_path,
        output_path,
        parameters=parameters
    )

# Pipeline logic: run notebook and return file content
def run_pipeline_logic(milestone, params):
    notebook_path = "your_notebook.ipynb"
    output_path = f"executed_{milestone}.ipynb"
    
    run_notebook(notebook_path, output_path, params)

    with open(output_path, "rb") as f:
        file_data = f.read()

    return file_data

# API route
@app.post("/run-pipeline")
async def run_pipeline(request: RunPipelineRequest):
    milestone = request.milestone
    params = request.params

    try:
        file_data = run_pipeline_logic(milestone, params)

        file_id = fs.put(file_data, filename=f"Report_{milestone}.ipynb")

        report_data = {
            "milestone": milestone,
            "date_generated": datetime.now().isoformat(),
            "status": "Completed",
            "result_type": "Notebook",
            "file_name": f"Report_{milestone}.ipynb",
            "file_data": {"file_id": file_id},
            "metadata": {"execution_time": "Simulated"}
        }

        reports_collection.insert_one(report_data)

        return {
            "status": "success",
            "message": f"Pipeline for '{milestone}' executed successfully.",
            "file_id": str(file_id)
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Pipeline failed: {str(e)}"
        }

# Run locally or via uvicorn in Docker
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
