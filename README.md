# TaskFlow API

A lightweight project & task management REST API built with **FastAPI**.

## Quick Start

```bash
cd sample_app
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| POST | `/api/users/` | User signup |
| GET | `/api/projects/` | List all projects |
| POST | `/api/projects/` | Create a project |
| GET | `/api/projects/{id}` | Get project details |
| PATCH | `/api/projects/{id}` | Update a project |
| DELETE | `/api/projects/{id}` | Delete a project |
| GET | `/api/tasks/` | List tasks (filter by project/status) |
| POST | `/api/tasks/` | Create a task |
| GET | `/api/tasks/{id}` | Get task details |
| PATCH | `/api/tasks/{id}` | Update a task |
| DELETE | `/api/tasks/{id}` | Delete a task |
| GET | `/api/projects/{id}/health` | **Project health report** |

## User Signup

To create a new user account:

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "password": "securepassword123"}'
```

Features:
- Unique username enforcement
- Secure password hashing (bcrypt)
- Automatic timestamp tracking
- Input validation

## Deploy to Render

1. Push this folder to a GitHub repo.
2. Connect the repo on [render.com](https://render.com).
3. Render will auto-detect `render.yaml` and deploy.

## Known Issue

`GET /api/projects/1/health` crashes with an `AttributeError` when the project contains unassigned tasks. See the linked Jira ticket for details.