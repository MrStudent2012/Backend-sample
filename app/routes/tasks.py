"""Task routes for the TaskFlow API."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..database import (
    create_task,
    delete_task,
    get_project,
    get_task,
    list_tasks,
    update_task,
)
from ..models import Task, TaskCreate, TaskStatus, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("/", response_model=List[Task])
def get_tasks(
    project_id: Optional[int] = Query(None, description="Filter by project"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
):
    """List tasks, optionally filtered by project and/or status."""
    tasks = list_tasks(project_id=project_id)
    if status is not None:
        tasks = [t for t in tasks if t["status"] == status.value]
    return tasks


@router.get("/{task_id}", response_model=Task)
def get_task_by_id(task_id: int):
    """Retrieve a single task by ID."""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/", response_model=Task, status_code=201)
def create_new_task(project_id: int, body: TaskCreate):
    """Create a new task inside a project."""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    task = create_task(
        project_id=project_id,
        title=body.title,
        description=body.description,
        assignee=body.assignee,
        priority=body.priority,
        due_date=body.due_date,
        labels=body.labels,
    )
    return task


@router.patch("/{task_id}", response_model=Task)
def update_existing_task(task_id: int, body: TaskUpdate):
    """Update an existing task."""
    fields = body.model_dump(exclude_unset=True)
    if "status" in fields and fields["status"] is not None:
        fields["status"] = fields["status"].value if hasattr(fields["status"], "value") else fields["status"]
    updated = update_task(task_id, **fields)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/{task_id}", status_code=204)
def delete_existing_task(task_id: int):
    """Delete a task."""
    if not delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")