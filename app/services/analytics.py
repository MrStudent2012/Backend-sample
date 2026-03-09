"""Analytics service for project health reports.

Aggregates task data per project and produces a health score
along with a human-readable report for stakeholders.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from ..database import list_tasks, get_project
from ..models import (
    MemberWorkload,
    ProjectHealth,
    TaskSummary,
    TaskStatus,
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def calculate_project_health(project_id: int) -> ProjectHealth:
    """Build a full health report for *project_id*.

    Raises ``ValueError`` if the project does not exist.
    """
    project = get_project(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    tasks = list_tasks(project_id=project_id)
    summary = _build_summary(tasks)
    workloads = _build_workloads(tasks)
    health_score = _compute_health_score(summary)
    report = _format_report(project, tasks, summary, workloads)

    return ProjectHealth(
        project_id=project["id"],
        project_name=project["name"],
        summary=summary,
        member_workloads=workloads,
        health_score=health_score,
        report=report,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _build_summary(tasks: List[Dict[str, Any]]) -> TaskSummary:
    total = len(tasks)
    todo = sum(1 for t in tasks if t["status"] == TaskStatus.TODO.value)
    in_progress = sum(1 for t in tasks if t["status"] == TaskStatus.IN_PROGRESS.value)
    in_review = sum(1 for t in tasks if t["status"] == TaskStatus.IN_REVIEW.value)
    done = sum(1 for t in tasks if t["status"] == TaskStatus.DONE.value)
    completion_rate = round(done / total * 100, 1) if total else 0.0

    now = datetime.utcnow()
    overdue = sum(
        1 for t in tasks
        if t.get("due_date") and t["due_date"] < now and t["status"] != TaskStatus.DONE.value
    )

    return TaskSummary(
        total=total,
        todo=todo,
        in_progress=in_progress,
        in_review=in_review,
        done=done,
        completion_rate=completion_rate,
        overdue=overdue,
    )


def _build_workloads(tasks: List[Dict[str, Any]]) -> List[MemberWorkload]:
    """Aggregate per-member statistics."""
    members: Dict[str, Dict[str, int]] = {}
    for task in tasks:
        member = task.get("assignee") or "UNASSIGNED"                    # <-- can be None!
        members.setdefault(member, {"assigned": 0, "completed": 0, "in_progress": 0})
        members[member]["assigned"] += 1
        if task["status"] == TaskStatus.DONE.value:
            members[member]["completed"] += 1
        elif task["status"] == TaskStatus.IN_PROGRESS.value:
            members[member]["in_progress"] += 1

    return [
        MemberWorkload(
            member=name,
            assigned=stats["assigned"],
            completed=stats["completed"],
            in_progress=stats["in_progress"],
        )
        for name, stats in members.items()
    ]


def _compute_health_score(summary: TaskSummary) -> float:
    """Return a 0-100 health score: higher is better."""
    if summary.total == 0:
        return 100.0
    score = summary.completion_rate
    # Penalise overdue tasks
    overdue_penalty = (summary.overdue / summary.total) * 30
    score = max(0.0, score - overdue_penalty)
    return round(score, 1)


# ──────────────────────────────────────────────────────────────────────────
#  BUG IS HERE 🐛
#  `task["assignee"]` can be None for unassigned tasks.
#  Calling `.upper()` on None raises:
#      AttributeError: 'NoneType' object has no attribute 'upper'
#
#  FIX: guard with `task["assignee"] or "Unassigned"`
# ──────────────────────────────────────────────────────────────────────────

def _format_report(
    project: Dict[str, Any],
    tasks: List[Dict[str, Any]],
    summary: TaskSummary,
    workloads: List[MemberWorkload],
) -> str:
    """Build a human-readable health report string."""
    lines: List[str] = [
        f"=== Project Health Report: {project['name']} ===",
        f"Owner       : {project['owner']}",
        f"Total tasks : {summary.total}",
        f"Completed   : {summary.done} ({summary.completion_rate}%)",
        f"Overdue     : {summary.overdue}",
        "",
        "--- Task Breakdown ---",
    ]

    for task in tasks:
        status_icon = {
            TaskStatus.TODO.value: "⬚",
            TaskStatus.IN_PROGRESS.value: "▶",
            TaskStatus.IN_REVIEW.value: "🔍",
            TaskStatus.DONE.value: "✔",
        }.get(task["status"], "?")

        # 🐛 BUG: task["assignee"] is None for unassigned tasks.
        #    .upper() on None → AttributeError
        assignee_display = (task.get("assignee") or "UNASSIGNED").upper()

        priority_tag = f'[{task["priority"].upper()}]'
        lines.append(
            f'  {status_icon} {task["title"]:<40} '
            f'{priority_tag:<10} Assigned to: {assignee_display}'
        )

    lines.append("")
    lines.append("--- Member Workloads ---")
    for wl in workloads:
        lines.append(
            f"  {wl.member}: {wl.assigned} assigned, "
            f"{wl.completed} done, {wl.in_progress} active"
        )

    return "\n".join(lines)
