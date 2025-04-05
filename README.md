# Technician Scenarios Execution & Deployment Pipeline

This repository contains a structured Jupyter notebook workflow designed to execute technician scenario checklists in a sequential cloud-based pipeline and deploy the output to a Heroku app.

---

## 📁 Project Structure


---

## 🔁 Workflow Automation

### 1. Notebook Execution

The `execute-workflow.yml` GitHub Action will:

- Automatically run all 12 Jupyter notebooks in numerical order.
- Fail fast if any notebook execution results in an error.
- Optionally commit and push executed notebooks (editable inside the action if needed).

### 2. Heroku Deployment

The `deploy.yml` GitHub Action:

- Installs dependencies from `requirements.txt`.
- Pushes the latest app to Heroku.
- Triggered by every push to the `main` branch.
