"""In-memory database for the TaskFlow API.

Uses simple dicts so the app runs without external dependencies.
Replace with SQLAlchemy / PostgreSQL for production.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .models import Priority, TaskStatus
from .models import UserInDB


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------

_projects: Dict[int, Dict[str, Any]] = {}
_tasks: Dict[int, Dict[str, Any]] = {}
_users: Dict[int, Dict[str, Any]] = {}
_next_project_id: int = 1
_next_task_id: int = 1
_next_user_id: int = 1


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

def seed_database() -> None:
    """Populate the database with sample data for demonstration."""
    global _next_project_id, _next_task_id

    # ---- Project 1 ----
    p1 = create_project("TaskFlow Backend", "Core API services", "alice")

    create_task(p1["id"], "Set up FastAPI skeleton", assignee="alice",
                status=TaskStatus.DONE, priority=Priority.HIGH,
                completed_at=datetime.utcnow() - timedelta(days=10))

    create_task(p1["id"], "Implement authentication middleware", assignee="bob",
                status=TaskStatus.IN_PROGRESS, priority=Priority.HIGH,
                due_date=datetime.utcnow() + timedelta(days=2))

    create_task(p1["id"], "Add rate limiting", assignee=None,       # <-- unassigned!
                status=TaskStatus.TODO, priority=Priority.MEDIUM,
                due_date=datetime.utcnow() + timedelta(days=7))

    create_task(p1["id"], "Write unit tests for task CRUD", assignee="charlie",
                status=TaskStatus.IN_REVIEW, priority=Priority.MEDIUM,
                due_date=datetime.utcnow() - timedelta(days=1))       # overdue!

    create_task(p1["id"], "Database migration script", assignee=None,  # <-- unassigned!
                status=TaskStatus.TODO, priority=Priority.LOW,
                due_date=datetime.utcnow() + timedelta(days=14))

    # ---- Project 2 ----
    p2 = create_project("TaskFlow Frontend", "React dashboard", "dave")

    create_task(p2["id"], "Design dashboard wireframes", assignee="eve",
                status=TaskStatus.DONE, priority=Priority.HIGH,
                completed_at=datetime.utcnow() - timedelta(days=5))

    create_task(p2["id"], "Implement project list view", assignee="dave",
                status=TaskStatus.IN_PROGRESS, priority=Priority.HIGH,
                due_date=datetime.utcnow() + timedelta(days=3))

    create_task(p2["id"], "Add drag-and-drop task reorder", assignee=None,  # unassigned
                status=TaskStatus.TODO, priority=Priority.LOW)


# ---------------------------------------------------------------------------
# Project CRUD
# ---------------------------------------------------------------------------

def create_project(name: str, description: str = "", owner: str = "") -> Dict[str, Any]:
    global _next_project_id
    now = datetime.utcnow()
    project = {
        "id": _next_project_id,
        "name": name,
        "description": description,
        "owner": owner,
        "created_at": now,
        "updated_at": now,
    }
    _projects[_next_project_id] = project
    _next_project_id += 1
    return project


def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    return _projects.get(project_id)


def list_projects() -> List[Dict[str, Any]]:
    return list(_projects.values())


def update_project(project_id: int, **fields: Any) -> Optional[Dict[str, Any]]:
    project = _projects.get(project_id)
    if not project:
        return None
    for k, v in fields.items():
        if v is not None:
            project[k] = v
    project["updated_at"] = datetime.utcnow()
    return project


def delete_project(project_id: int) -> bool:
    if project_id in _projects:
        del _projects[project_id]
        # cascade delete tasks
        to_remove = [tid for tid, t in _tasks.items() if t["project_id"] == project_id]
        for tid in to_remove:
            del _tasks[tid]
        return True
    return False


# ---------------------------------------------------------------------------
# Task CRUD
# ---------------------------------------------------------------------------

def create_task(
    project_id: int,
    title: str,
    description: str = "",
    assignee: Optional[str] = None,
    status: TaskStatus = TaskStatus.TODO,
    priority: Priority = Priority.MEDIUM,
    due_date: Optional[datetime] = None,
    completed_at: Optional[datetime] = None,
    labels: Optional[List[str]] = None,
) -> Dict[str, Any]:
    global _next_task_id
    now = datetime.utcnow()
    task = {
        "id": _next_task_id,
        "project_id": project_id,
        "title": title,
        "description": description,
        "assignee": assignee,
        "status": status.value if isinstance(status, TaskStatus) else status,
        "priority": priority.value if isinstance(priority, Priority) else priority,
        "created_at": now,
        "updated_at": now,
        "completed_at": completed_at,
        "due_date": due_date,
        "labels": labels or [],
    }
    _tasks[_next_task_id] = task
    _next_task_id += 1
    return task


def get_task(task_id: int) -> Optional[Dict[str, Any]]:
    return _tasks.get(task_id)


def list_tasks(project_id: Optional[int] = None) -> List[Dict[str, Any]]:
    tasks = list(_tasks.values())
    if project_id is not None:
        tasks = [t for t in tasks if t["project_id"] == project_id]
    return tasks


def update_task(task_id: int, **fields: Any) -> Optional[Dict[str, Any]]:
    task = _tasks.get(task_id)
    if not task:
        return None
    for k, v in fields.items():
        if v is not None:
            task[k] = v
    task["updated_at"] = datetime.utcnow()
    # auto-set completed_at
    if fields.get("status") == TaskStatus.DONE.value or fields.get("status") == TaskStatus.DONE:
        task["completed_at"] = datetime.utcnow()
    return task


def delete_task(task_id: int) -> bool:
    if task_id in _tasks:
        del _tasks[task_id]
        return True
    return False


# ---------------------------------------------------------------------------
# User CRUD
# ---------------------------------------------------------------------------

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Retrieve a user by their username."""
    for user_data in _users.values():
        if user_data["username"] == username:
            return user_data
    return None


def create_user(username: str, hashed_password: str) -> Dict[str, Any]:
    """Create a new user record in the database."""
    global _next_user_id
    now = datetime.utcnow()
    user_data = UserInDB(
        id=_next_user_id,
        username=username,
        hashed_password=hashed_password,
        created_at=now,
    ).model_dump()
    
    _users[_next_user_id] = user_data
    _next_user_id += 1
    return user_data


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a user by their ID."""
    return _users.get(user_id)