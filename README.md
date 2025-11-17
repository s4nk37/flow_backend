# Flow Todo Backend

AA lightweight, modular FastAPI backend for managing Todo items.
Built with Poetry, SQLAlchemy, Pydantic, and Alembic, following a clean, scalable project structure.
This backend powers the Flow mobile app.

## 🚀 Features

- FastAPI-based REST API
- SQLAlchemy ORM + Alembic migrations
- Pydantic request/response models
- Modular routing (versioned API)
- CRUD endpoints for Todo items
- Ready for deployment (Uvicorn / Gunicorn)
- Poetry for dependency + environment management
- Clear project layout to ease extension and DB integration
- Tests with pytest

## 📦 Tech Stack

- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- Poetry
- SQLite / PostgreSQL (future-ready)

## 📁 Project Structure

```
flow_backend/
├── alembic
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
├── alembic.ini
├── app
│   ├── __init__.py
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   └── __init__.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── database.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── main.py
│   ├── models/
│   │   └── todo.py
│   ├── routes/
│   │   └── todo.py
│   ├── schemas/
│   │   ├── todo.py
│   │   └── todos_response.py
│   └── utils/
│       └── logger.py
├── LICENSE
├── poetry.lock
├── pyproject.toml
└── README.md
```

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

2. Install Poetry

```bash
pip install poetry
```

3. Install dependencies & activate virtual environment

```bash
poetry install
poetry shell
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

## 🤝 Contributing

- Open issues for bugs or enhancements

- Submit focused PRs

- Ensure code is formatted (black, isort recommended)

## 📄 License

MIT License — see LICENSE.
