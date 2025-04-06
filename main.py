from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/run-checklist-conversion")
def run_checklist_conversion():
    try:
        # Run the script and capture the output
        result = subprocess.run(["python", "1_test_converting_a_checklist.py"], capture_output=True, text=True)

        return {
            "status": "success" if result.returncode == 0 else "error",
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
