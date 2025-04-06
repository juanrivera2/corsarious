from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
import gridfs
from datetime import datetime
import papermill as pm
import os

# Initialize FastAPI app
app = FastAPI()

# MongoDB connection (replace with your MongoDB Atlas URI if needed)
client = MongoClient("mongodb+srv://AIDatabase:BTColombia2022@sandbox.bxohv.mongodb.net/?retryWrites=true&w=majority&appName=sandbox")
db = client['AIDatabase']
fs = gridfs.GridFS(db)
reports_collection = db['Reports']

# Request model for pipeline
class RunPipelineRequest(BaseModel):
    milestone: str
    params: dict

# Function to run the Jupyter notebook using Papermill
def run_notebook(notebook_path: str, output_path: str, parameters: dict):
    """
    Executes a Jupyter notebook with provided parameters and stores the result.
    :param notebook_path: Path to the notebook to be executed
    :param output_path: Path where the executed notebook will be saved
    :param parameters: Parameters to pass into the notebook
    """
    pm.execute_notebook(
        notebook_path,      # Path to your notebook
        output_path,        # Path to save the executed notebook
        parameters=parameters  # Parameters for the notebook
    )

# Simulated pipeline logic (can be replaced with actual notebook execution logic)
def run_pipeline_logic(milestone, params):
    # Placeholder: Run the notebook with provided parameters
    output_notebook_path = f"output_{milestone}.ipynb"  # Path to store the executed notebook
    notebook_path = "your_notebook.ipynb"  # Path to the notebook you want to run
    
    # Execute the notebook using papermill
    run_notebook(notebook_path, output_notebook_path, params)
    
    # After executing the notebook, you can read any generated output (e.g., PDF, report)
    # For this example, assume the notebook generates a report file, or a PDF
    with open(output_notebook_path, "rb") as file:
        file_data = file.read()
    
    return file_data

# API route to trigger pipeline
@app.post("/run-pipeline")
async def run_pipeline(request: RunPipelineRequest):
    milestone = request.milestone
    params = request.params

    # Run pipeline logic (this will execute the Jupyter notebook and generate output)
    file_data = run_pipeline_logic(milestone, params)

    # Save binary file (PDF or other result) to MongoDB using GridFS
    file_id = fs.put(file_data, filename=f"Report_{milestone}.pdf")

    # Save report metadata to 'Reports' collection
    report_data = {
        "milestone": milestone,
        "date_generated": datetime.now().isoformat(),
        "status": "Completed",
        "result_type": "PDF",  # Or whatever the result type is
        "file_name": f"Report_{milestone}.pdf",
        "file_data": {"file_id": file_id},
        "metadata": {"execution_time": "Simulated"}  # Customize if needed
    }
    reports_collection.insert_one(report_data)

    return {
        "status": "success",
        "message": f"Pipeline for '{milestone}' executed successfully.",
        "file_id": str(file_id)
    }
