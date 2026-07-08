# Jira Ticket — Ready to feed to the Agent Pipeline

> Copy-paste the fields below into your Jira instance (or pass the
> description directly to the resolver CLI).

---

## Ticket ID
**TASKFLOW-143**

## Title
Implement User Signup with Basic User Record Creation

## Type
Feature

## Priority
Medium

## Component
`taskflow-api` / User Management

## Environment
- **Service**: TaskFlow API v1.2.0
- **Runtime**: Python 3.11 / FastAPI 0.110
- **OS**: Ubuntu 22.04 (Render.com web service)
- **Endpoint**: `POST /api/users/` (to be created)

## Description

Implement a signup feature that creates a new user record when a user successfully registers in our backend-sample service.

### Requirements

- Create a new user record upon successful signup.
- Store only the minimum required user information:
  - Username
  - Password (stored securely as a hashed value)
  - Account creation timestamp
- Ensure the username is unique.
- Validate required fields before creating the user.
- Return an appropriate success or error response based on the outcome.

### Acceptance Criteria

- A new user record is created after successful signup.
- Only the following fields are stored:
  - Username
  - Hashed password
  - Created timestamp
- Duplicate usernames are rejected with an appropriate error message.
- Passwords are never stored in plain text.
- The API returns a success response when the account is created successfully.
- Invalid or incomplete signup requests return appropriate validation errors.

### Implementation Steps

1. **Add Dependencies** (`requirements.txt`):
   - Add `passlib[bcrypt]>=1.7.0` for secure password hashing
   - Ensure `sqlalchemy>=1.4.0` is present

2. **Create User Model** (`app/models.py`):
   - Define `User` class inheriting from `Base`
   - Fields: `id`, `username` (unique, indexed), `hashed_password`, `created_at`
   - Username must be unique and indexed for fast lookups

3. **Create User Schemas** (`app/schemas.py`):
   - `UserCreate`: for signup requests (username, password)
   - `UserResponse`: for API responses (id, username, created_at)
   - Validate required fields

4. **Password Hashing Utility** (`app/auth.py` or similar):
   - Use `passlib` with bcrypt to hash passwords
   - Provide `get_password_hash()` and `verify_password()` functions

5. **CRUD Operations** (`app/crud.py`):
   - `create_user()`: create new user with hashed password
   - `get_user_by_username()`: check for existing usernames
   - Handle database transactions properly

6. **API Endpoint** (`app/main.py`):
   - `POST /api/users/` endpoint
   - Validate input with `UserCreate` schema
   - Check for duplicate username
   - Hash password before storing
   - Return `UserResponse` on success (201 Created)
   - Return appropriate errors for duplicates (409 Conflict) or validation failures (422 Unprocessable Entity)

7. **Database Migration**:
   - Create migration script to add `users` table
   - Ensure table is created with proper indexes and constraints

### Expected Behaviour

```bash
# Successful signup
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "SecurePass123!"}'

# Response: 201 Created
{
  "id": 1,
  "username": "john_doe",
  "created_at": "2026-07-07T18:12:34.567890Z"
}

# Duplicate username attempt
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "password": "AnotherPass456"}'

# Response: 409 Conflict
{
  "detail": "Username already exists"
}

# Invalid input
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": ""}'

# Response: 422 Unprocessable Entity
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Security Considerations

- Passwords must NEVER be stored in plain text
- Use bcrypt with appropriate work factor (default 12 rounds)
- Usernames should be case-sensitive or normalized consistently
- Consider rate limiting for signup endpoint (future enhancement)
- Validate password strength (optional for MVP)

### Files to Modify

1. `requirements.txt` - Add password hashing library
2. `app/models.py` - Add User model
3. `app/schemas.py` - Add UserCreate and UserResponse schemas
4. `app/auth.py` - Create password hashing utilities (new file)
5. `app/crud.py` - Add user CRUD operations (new file or extend existing)
6. `app/main.py` - Add POST /api/users/ endpoint
7. `app/database.py` - Ensure Base and get_db are properly configured
8. Migration script - Create users table

---

## CLI Command to Run the Agent

```bash
python -m jira_resolver_mcp TASKFLOW-143 \
    --description "Implement user signup endpoint POST /api/users/ with username uniqueness check, bcrypt password hashing, and basic user record creation. Requirements: Store username, hashed_password, created_at. Return 201 on success, 409 for duplicate username, 422 for validation errors. Files: app/models.py (User model), app/schemas.py (UserCreate, UserResponse), app/auth.py (password hashing), app/crud.py (user operations), app/main.py (endpoint), requirements.txt (add passlib[bcrypt]). Environment: Python 3.11, FastAPI 0.110, SQLAlchemy, Ubuntu 22.04."
```

This description provides complete context for the agent pipeline:

| Agent | What it extracts |
|-------|-----------------|
| **Ticket Agent** | ✅ Complete feature requirements with acceptance criteria. Extracts hints: `app/models.py`, `app/schemas.py`, `app/auth.py`, `app/crud.py`, `app/main.py`, `requirements.txt` |
| **Navigator Agent** | Hints lead to correct files in `sample_app` repo; identifies new files to create and existing files to modify |
| **Implementer Agent** | Clear specifications for each file change: model structure, schema definitions, endpoint logic, security requirements |
| **Reviewer Agent** | Can verify password hashing is used, unique constraint exists, proper HTTP status codes returned |
| **Human Approval** | Feature implementation is reviewable with clear acceptance criteria |
| **GitHub Ops** | Creates branch `jira/TASKFLOW-143-*`, applies changes, opens PR |