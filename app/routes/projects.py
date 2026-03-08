"""Project routes for the TaskFlow API."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from ..database import (
    create_project,
    delete_project,
    get_project,
    list_projects,
    update_project,
)
from ..models import Project, ProjectCreate, ProjectUpdate

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("/", response_model=List[Project])
def get_projects():
    """List all projects."""
    return list_projects()


@router.get("/{project_id}", response_model=Project)
def get_project_by_id(project_id: int):
    """Retrieve a single project by ID."""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=Project, status_code=201)
def create_new_project(body: ProjectCreate):
    """Create a new project."""
    project = create_project(
        name=body.name,
        description=body.description,
        owner=body.owner,
    )
    return project


@router.patch("/{project_id}", response_model=Project)
def update_existing_project(project_id: int, body: ProjectUpdate):
    """Update an existing project."""
    updated = update_project(
        project_id,
        name=body.name,
        description=body.description,
        owner=body.owner,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated


@router.delete("/{project_id}", status_code=204)
def delete_existing_project(project_id: int):
    """Delete a project and all its tasks."""
    if not delete_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
