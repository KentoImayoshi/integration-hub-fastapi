# Integration Hub (MVP)

A lightweight **Integration Hub** built with **FastAPI + Postgres** that runs connector-based jobs asynchronously, tracks **executions/attempts**, and supports **retries**.

This project is designed as a portfolio-friendly foundation for building real integrations (e.g., SpaceX APIs, webhooks, ETL triggers, internal systems) using a plugin-style connector architecture.

---

## Features

- **Job orchestration**
  - `POST /jobs` creates a job and starts **attempt 1**
  - `POST /jobs/{job_id}/retry` creates **attempt N+1**
- **Execution tracking**
  - Each attempt is stored in `job_executions` (status, timestamps, output, error)
- **Connector registry**
  - Run jobs by `connector_name` (plugin pattern)
  - Example connector: `echo`
- **Filtering & pagination**
  - `GET /jobs?status=SUCCESS&connector_name=echo&limit=50&offset=0`

---

## Tech Stack

- Python + FastAPI
- SQLAlchemy
- Postgres (Docker)
- Connector registry (plugin-style design)

---

## Project Structure

```text
spacex-integration-hub/
├── app/
│ ├── connectors/
│ │ ├── init.py
│ │ ├── base.py
│ │ ├── echo.py
│ │ └── registry.py
│ ├── db.py
│ ├── main.py
│ └── models.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## How to Run

### 1) Start infrastructure (Postgres)
docker compose up -d

### 2) Create & activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

### 3) Start the API
uvicorn app.main:app --reload

### 4) Open API docs
Swagger UI: http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/health

### API Usage (PowerShell)
#### Create a job (echo connector)

```text
$body = @{ connector_name = "echo"; payload = @{ msg = "hello" } } | ConvertTo-Json -Depth 5

$job = Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/jobs" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
$job
```

#### Check job status (includes executions)

Start-Sleep 2
Invoke-RestMethod "http://127.0.0.1:8000/jobs/$($job.job_id)"

#### Retry a job (creates attempt 2, 3, ...)
$retry = Invoke-RestMethod -Uri "http://127.0.0.1:8000/jobs/$($job.job_id)/retry" -Method POST
$retry

Start-Sleep 2
Invoke-RestMethod "http://127.0.0.1:8000/jobs/$($job.job_id)"

#### List jobs with filters + pagination
Invoke-RestMethod "http://127.0.0.1:8000/jobs?status=SUCCESS&connector_name=echo&limit=10&offset=0"

#### Try an unknown connector (should fail)
$body = @{ connector_name = "nope"; payload = @{ msg = "should fail" } } | ConvertTo-Json -Depth 5
$job2 = Invoke-RestMethod -Uri "http://127.0.0.1:8000/jobs" -Method POST -ContentType "application/json" -Body $body

Start-Sleep 2
Invoke-RestMethod "http://127.0.0.1:8000/jobs/$($job2.job_id)"

## Database Model (High Level)
### jobs
#### id, connector_name, status, payload, created_at, updated_at

### job_executions
#### id, job_id, attempt, status, started_at, finished_at, output, error_message

## Roadmap
Add a real SpaceX connector (e.g., latest launches)

Add Alembic migrations (versioned schema)

Add a proper job queue (Celery + Redis) instead of FastAPI background tasks

Add authentication / API keys

Add structured logging + observability

## License
This project is licensed under the MIT License. See LICENSE.