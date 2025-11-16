# flow_backend

A lightweight, modular FastAPI backend for managing Todo items. Built as a learning project to demonstrate clean structure, Pydantic models, routing, and basic CRUD operations with future SQLite support. This service is intended to power the Flow mobile app.

## Features

- FastAPI-based REST API
- Pydantic request/response models
- CRUD endpoints for Todo items
- Clear project layout to ease extension and DB integration
- Tests with pytest

## Prerequisites (macOS)

- Python 3.10+ (or compatible)
- git
- Optional: virtualenv / venv

## Quick start (macOS)

1. Clone and enter project

```bash
git clone <repo-url>
cd flow_backend
```

2. Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Run the development server

```bash
uvicorn app.main:app --reload
# or, if your entrypoint differs, adjust the module path
```

5. Open the interactive docs

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API (typical endpoints)

- GET /todos — list todos
- POST /todos — create a todo
- GET /todos/{id} — get todo by id
- PUT /todos/{id} — update todo
- DELETE /todos/{id} — delete todo

Example create:

```bash
curl -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk","completed":false}'
```

## Tests

Run unit tests:

```bash
pytest -q
```

## Contributing

- Open issues for bugs or enhancement requests
- Create small, focused PRs with tests where applicable

## License

MIT License — see LICENSE file (or add one if missing).
