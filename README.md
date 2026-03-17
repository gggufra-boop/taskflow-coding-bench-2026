# TaskFlow API

A task management API for teams, built with FastAPI and SQLAlchemy.

## Features

- **Projects**: Organize work into projects with unique slugs
- **Users**: Team members with roles (admin, member, viewer)
- **Tasks**: Create, assign, and track tasks with status workflows
- **Status transitions**: Enforced workflow (todo → in_progress → in_review → done)
- **Filtering**: List tasks by project, status, assignee, priority
- **Stats**: Per-project task breakdown by status

## Quick Start

```bash
pip install -e .
uvicorn app.main:app --reload
```

## Running Tests

```bash
pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/tasks/ | Create a task |
| GET | /api/v1/tasks/ | List tasks (with filters) |
| GET | /api/v1/tasks/{id} | Get a task |
| PATCH | /api/v1/tasks/{id} | Update a task |
| DELETE | /api/v1/tasks/{id} | Delete a task |
| GET | /api/v1/tasks/projects/{id}/stats | Project task stats |
| POST | /api/v1/users/ | Create a user |
| GET | /api/v1/users/ | List users |
| GET | /api/v1/users/{id} | Get a user |
| POST | /api/v1/projects/ | Create a project |
| GET | /api/v1/projects/ | List projects |
| GET | /api/v1/projects/{id} | Get a project |
