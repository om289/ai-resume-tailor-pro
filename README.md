# AI Resume Tailor Pro

AI Resume Tailor Pro is a production-style LLM application that analyzes a resume against a job description, calculates an ATS-style keyword score, identifies matched and missing skills, generates truthful resume improvements, and creates a role-specific cover letter.

This is not only a prompt-wrapper demo. It includes local scoring, a web dashboard, JSON APIs, SQLite persistence, feedback collection, export, fine-tuning dataset preparation, dataset validation, evaluation scripts, deployment files, and tests.

## Problem Statement

Students and job seekers often submit the same resume for every job. This reduces keyword alignment and makes strong experience harder for recruiters or ATS systems to notice. This project helps users tailor their resume honestly for a target role without inventing experience.

## Core Features

- Flask web dashboard
- Resume and job description input
- Role presets for Backend, Frontend, Data Analyst, and AI/ML Intern
- ATS-style keyword match score
- Matched and missing keyword analysis
- Section-level scoring
- Local analysis mode without an API key
- LLM-powered resume tailoring and cover letter generation
- Base model and fine-tuned model profile support
- JSON API endpoints for integrations
- SQLite-backed run history
- Feedback collection for model improvement
- Metrics endpoint
- TXT export for generated results
- Fine-tuning-ready JSONL dataset
- Dataset validation script
- Training example builder script
- Evaluation dataset and keyword recall script
- Production WSGI entrypoint
- Dockerfile and Docker Compose config
- Security headers and request size limits
- Unit tests

## Tech Stack

- Python
- Flask
- SQLite
- OpenAI-compatible Python SDK
- HTML and CSS
- JSONL for fine-tuning data
- Gunicorn for production-style Linux deployment

## Folder Structure

```text
resume_tailor/
  app.py
  wsgi.py
  Dockerfile
  docker-compose.yml
  README.md
  requirements.txt
  .env.example
  .gitignore
  config/
    fine_tuning_plan.json
  data/
    train_examples.jsonl
    eval_cases.jsonl
  docs/
    api.md
    deployment.md
    fine_tuning_workflow.md
    privacy_and_safety.md
  examples/
    resume.txt
    job_description.txt
  scripts/
    build_training_example.py
    evaluate_keyword_recall.py
    export_feedback.py
    init_db.py
    validate_dataset.py
  static/
    style.css
  storage/
    .gitkeep
  templates/
    index.html
  tests/
    test_matching.py
```

## Architecture

```text
User
  |
  v
Flask Web UI / JSON API / CLI
  |
  v
Input Validation + Resume/Job Processing
  |
  v
Keyword Extraction + ATS Match Scoring
  |
  +------> Local Tailoring Summary
  |
  v
Prompt Builder
  |
  v
Base Model or Fine-Tuned Model
  |
  v
Tailored Output + Export
  |
  v
SQLite Runs + Feedback + Fine-Tuning Dataset + Evaluation Pipeline
```

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Set API variables if you want LLM generation:

```powershell
$env:AI_API_KEY="your_api_key_here"
$env:AI_BASE_URL="https://api.hke-cai.com/inference/v1"
$env:AI_MODEL="deepseek/deepseek-v4-pro"
$env:AI_FINE_TUNED_MODEL="your_fine_tuned_model_here"
```

You can also create a local `.env` file from `.env.example`. Do not upload your real API key to GitHub.

## Run The Web App

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5002
```

Use local analysis without the API key, or enable **Use LLM API** after setting `AI_API_KEY`.

The **Model Profile** control lets you switch between the base model and a future fine-tuned model. Set `AI_FINE_TUNED_MODEL` after your provider gives you the fine-tuned model name.

## CLI Usage

Local mode:

```powershell
python app.py --resume examples/resume.txt --job examples/job_description.txt --role backend
```

LLM mode:

```powershell
python app.py --resume examples/resume.txt --job examples/job_description.txt --role backend --use-ai
```

Fine-tuned model profile:

```powershell
python app.py --resume examples/resume.txt --job examples/job_description.txt --role backend --use-ai --model-profile fine_tuned
```

Validate fine-tuning data:

```powershell
python app.py --validate-data
```

## JSON API

Full docs are in:

```text
docs/api.md
```

Important endpoints:

```text
POST /api/analyze
GET /api/runs
GET /api/runs/<run_id>
POST /api/feedback
GET /health
GET /metrics
GET /export/<run_id>.txt
```

Example request:

```json
{
  "resume_text": "Python intern with Flask and SQL experience.",
  "job_text": "Junior backend developer with Python, Flask, SQL, APIs, Git, and testing.",
  "role": "backend",
  "tone": "professional",
  "use_ai": false,
  "model_profile": "base"
}
```

## Fine-Tuning Pipeline

Training examples are stored in:

```text
data/train_examples.jsonl
```

Each line follows chat fine-tuning format:

```json
{"messages":[{"role":"system","content":"..."},{"role":"user","content":"Resume: ... Job: ..."},{"role":"assistant","content":"...ideal output..."}]}
```

Validate the dataset:

```powershell
python scripts/validate_dataset.py data/train_examples.jsonl
```

Append a new training example:

```powershell
python scripts/build_training_example.py --resume examples/resume.txt --job examples/job_description.txt --output ideal_output.txt
```

Evaluate keyword recall:

```powershell
python scripts/evaluate_keyword_recall.py data/eval_cases.jsonl
```

Export user feedback for future model improvement:

```powershell
python scripts/export_feedback.py
```

More notes:

```text
docs/fine_tuning_workflow.md
config/fine_tuning_plan.json
```

## Deployment

Deployment notes:

```text
docs/deployment.md
```

Docker:

```bash
docker compose up --build
```

Linux production-style run:

```bash
gunicorn --bind 0.0.0.0:5002 wsgi:app
```

## Privacy And Safety

Privacy notes are in:

```text
docs/privacy_and_safety.md
```

For demos, use sample resumes or remove personal contact details. Do not commit real resumes, API keys, or generated user history.

## Testing

Run tests:

```powershell
python -m unittest discover tests
```

## Production-Level Improvements Included

- Environment-variable based secret handling
- Optional local `.env` loading
- Health endpoint
- Metrics endpoint
- JSON API routes
- CLI mode
- SQLite saved run history
- Feedback collection
- Export route
- Dataset validation
- Evaluation script
- WSGI entrypoint
- Dockerfile and Docker Compose config
- Security headers and request size limits
- Modular scoring logic
- Tests
- GitHub-safe `.gitignore`

## Future Scope

- User authentication
- PostgreSQL for multi-user production
- PDF and DOCX parsing
- PDF/DOCX export
- Admin dashboard for reviewing training examples
- Human feedback rating analytics
- Base-model vs fine-tuned-model comparison page
- Background jobs for long model calls

## Project Summary

This project demonstrates how an LLM can be used as part of a larger AI product instead of as a simple chatbot. It combines prompt engineering, ATS scoring, API integration, persistence, feedback collection, data preparation, fine-tuning workflow design, evaluation, deployment planning, and practical web application development.
