from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
import gridfs
from datetime import datetime

# Initialize FastAPI app
app = FastAPI()

# MongoDB connection (replace with your MongoDB Atlas URI if needed)
client = MongoClient("mongodb://localhost:27017/")
db = client['AIDatabase']
fs = gridfs.GridFS(db)
reports_collection = db['Reports']

# Request model for pipeline
class RunPipelineRequest(BaseModel):
    milestone: str
    params: dict

# Simulated pipeline logic
def run_pipeline_logic(milestone, params):
    # Placeholder: Replace this with real pipeline execution
    fake_pdf_data = b"%PDF-1.4 simulated binary report data%"  # Simulate PDF binary
    return {"file_data": fake_pdf_data}

# API route to trigger pipeline
@app.post("/run-pipeline")
async def run_pipeline(request: RunPipelineRequest):
    milestone = request.milestone
    params = request.params

    # Run pipeline logic (replace this with actual logic)
    result = run_pipeline_logic(milestone, params)

    # Save binary file to MongoDB using GridFS
    file_id = fs.put(result['file_data'], filename=f"Report_{milestone}.pdf")

    # Save report metadata to 'Reports' collection
    report_data = {
        "milestone": milestone,
        "date_generated": datetime.now().isoformat(),
        "status": "Completed",
        "result_type": "PDF",
        "file_name": f"Report_{milestone}.pdf",
        "file_data": {"file_id": file_id},
        "metadata": {"execution_time": "Simulated"}
    }
    reports_collection.insert_one(report_data)

    return {
        "status": "success",
        "message": f"Pipeline for '{milestone}' executed successfully.",
        "file_id": str(file_id)
    }
