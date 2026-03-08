"""TaskFlow API — A project and task management REST service.

Deployable on Render.com as a Web Service.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import APP_ENV, APP_VERSION
from .database import seed_database
from .models import ProjectHealth
from .routes.projects import router as projects_router
from .routes.tasks import router as tasks_router
from .services.analytics import calculate_project_health


# ---------------------------------------------------------------------------
# Lifespan – seed demo data on startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_database()
    yield


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="TaskFlow API",
    version=APP_VERSION,
    description="Project & task management service with analytics.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Routers ----
app.include_router(projects_router)
app.include_router(tasks_router)


# ---- Analytics endpoint (triggers the bug) ----

@app.get("/api/projects/{project_id}/health", response_model=ProjectHealth)
def project_health(project_id: int):
    """Get a full health report for a project.

    This endpoint aggregates task statistics, per-member workloads,
    and a health score.  It also generates a human-readable report.
    """
    try:
        return calculate_project_health(project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ---- Root / health-check ----

@app.get("/")
def root():
    return {
        "service": "TaskFlow API",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
