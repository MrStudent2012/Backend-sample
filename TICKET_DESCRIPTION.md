# Jira Ticket — Ready to feed to the Agent Pipeline

> Copy-paste the fields below into your Jira instance (or pass the
> description directly to the resolver CLI).

---

## Ticket ID
**TASKFLOW-142**

## Title
`GET /api/projects/{id}/health` returns 500 — AttributeError on unassigned tasks

## Type
Bug

## Priority
High

## Component
`taskflow-api` / Analytics Service

## Environment
- **Service**: TaskFlow API v1.2.0
- **Runtime**: Python 3.11 / FastAPI 0.110
- **OS**: Ubuntu 22.04 (Render.com web service)
- **Endpoint**: `GET /api/projects/1/health`

## Description

The project health endpoint crashes with an **`AttributeError`** whenever the
target project contains one or more **unassigned tasks** (i.e. tasks where
`assignee` is `null`).

The endpoint works fine for projects where every task has an assignee, but
Project 1 ("TaskFlow Backend") has two unassigned tasks — "Add rate limiting"
and "Database migration script" — and any call to its health report fails.

### Reproduction Steps

1. Start the API server:
   ```
   cd sample_app
   uvicorn app.main:app --reload
   ```
2. Confirm seed data loaded:
   ```
   curl http://localhost:8000/api/tasks/?project_id=1
   ```
   → You will see tasks 3 and 5 have `"assignee": null`.
3. Trigger the bug:
   ```
   curl http://localhost:8000/api/projects/1/health
   ```
4. Server responds with **HTTP 500 Internal Server Error**.

### Error Logs / Stack Trace

```
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "app/main.py", line 63, in project_health
    return calculate_project_health(project_id)
  File "app/services/analytics.py", line 42, in calculate_project_health
    report = _format_report(project, tasks, summary, workloads)
  File "app/services/analytics.py", line 139, in _format_report
    assignee_display = task["assignee"].upper()
AttributeError: 'NoneType' object has no attribute 'upper'
```

### Expected Behaviour

`GET /api/projects/1/health` should return a **200** response with a full
`ProjectHealth` JSON payload.  Unassigned tasks should display
**"UNASSIGNED"** (or similar) in the report text instead of crashing.

### Actual Behaviour

Server returns a **500** response.  The `_format_report` function in
`app/services/analytics.py` calls `.upper()` on `task["assignee"]` without
checking for `None`.

### Suggested Fix Area

File: `app/services/analytics.py`, function `_format_report`, around line 139.

Replace:
```python
assignee_display = task["assignee"].upper()
```
with a null-safe alternative:
```python
assignee_display = (task["assignee"] or "Unassigned").upper()
```

### Additional Notes

There is also a secondary cosmetic issue in `_build_workloads` (same file,
line ~94): when `task["assignee"]` is `None`, the workload dict uses `None`
as a key which later gets serialised into the `MemberWorkload` model with
`member=None`.  The workload aggregation should map `None` → `"Unassigned"`
as well.

---

## CLI Command to Run the Agent

```bash
python -m jira_resolver_mcp TASKFLOW-142 \
    --description "GET /api/projects/{id}/health returns 500 — AttributeError: 'NoneType' object has no attribute 'upper' in app/services/analytics.py line 139. Reproduction: curl http://localhost:8000/api/projects/1/health on project with unassigned tasks (assignee=null). Stack trace: File app/services/analytics.py, line 139, in _format_report assignee_display = task['assignee'].upper(). Environment: Python 3.11, FastAPI 0.110, Ubuntu 22.04."
```

This description is engineered so that every agent in the pipeline has what
it needs:

| Agent | What it extracts |
|-------|-----------------|
| **Ticket Agent** | ✅ Logs/stack trace present → passes completeness check. Extracts hints: `app/services/analytics.py`, `app/main.py` |
| **Navigator Agent** | Hints lead to `sample_app` repo; `search_code_across_repos("app/services/analytics.py _format_report assignee")` narrows to the correct file |
| **Implementer Agent** | Clear description of what line to change and the expected fix pattern |
| **Reviewer Agent** | Patch should replace `.upper()` with `(... or "Unassigned").upper()` — passes review |
| **Human Approval** | Diff is small and reviewable |
| **GitHub Ops** | Creates branch `jira/TASKFLOW-142-*`, applies patch, opens PR |
