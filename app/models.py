"""Pydantic models for the TaskFlow API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ---------------------------------------------------------------------------
# Task models
# ---------------------------------------------------------------------------

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    assignee: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    due_date: Optional[datetime] = None
    labels: List[str] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assignee: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None
    labels: Optional[List[str]] = None


class Task(BaseModel):
    id: int
    project_id: int
    title: str
    description: str = ""
    assignee: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    labels: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Project models
# ---------------------------------------------------------------------------

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    owner: str = Field(..., min_length=1)


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None


class Project(BaseModel):
    id: int
    name: str
    description: str = ""
    owner: str
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Analytics / Health models
# ---------------------------------------------------------------------------

class TaskSummary(BaseModel):
    total: int
    todo: int
    in_progress: int
    in_review: int
    done: int
    completion_rate: float
    overdue: int


class MemberWorkload(BaseModel):
    member: str
    assigned: int
    completed: int
    in_progress: int


class ProjectHealth(BaseModel):
    project_id: int
    project_name: str
    summary: TaskSummary
    member_workloads: List[MemberWorkload]
    health_score: float
    report: str
