# full-auth-flask-backend-app

# Productivity Notes API (Flask Sessions)

A Flask REST API for a personal notes productivity tool. It provides session-based authentication and CRUD operations for notes. Every note belongs to its creator; authenticated users can only list, view, update, or delete their own notes.

## Technology

- Python 3.8+
- Flask 2.2.2
- Flask-SQLAlchemy 3.0.3
- Flask-Migrate 4.0.0
- Flask-Bcrypt 1.0.1
- Marshmallow 3.20.1
- SQLite by default (configurable with `DATABASE_URL`)
- Pytest 7.2.0

## Installation

1. Clone the repository and enter the project directory.
2. Install Pipenv if it is not installed:
   ```bash
   pip install pipenv
   ```
3. Install dependencies:
   ```bash
   pipenv install --dev
   ```
4. Copy `.env.example` to `.env`, then set a long random `SECRET_KEY`. Load the environment variables in your shell or use a dotenv loader of your choice. The app reads environment variables directly.
5. Activate the virtual environment:
   ```bash
   pipenv shell
   ```

## Database setup and migrations

Initialize migrations once:

```bash
flask --app app db init
```

Create and apply the first migration:

```bash
flask --app app db migrate -m "Create users and notes tables"
flask --app app db upgrade
```

After changing models, generate and apply another migration:

```bash
flask --app app db migrate -m "Describe model change"
flask --app app db upgrade
```

The default database is `instance/app.db` (Flask-SQLAlchemy's relative SQLite location). To use another database, set `DATABASE_URL`.

## Seed example data

```bash
python seed.py
```

This creates three demo users (`alice`, `bob`, `charlie`) and five notes for each. The demo password for all three users is `password123`. **Do not use these credentials in production.** The seed script clears existing notes and users before inserting demo records.

## Run the API

```bash
flask --app app run --debug
```

The API is available at `http://127.0.0.1:5000`.

## Session and frontend integration

The browser must retain and send the session cookie on subsequent requests. For `fetch`, use:

```javascript
fetch("http://127.0.0.1:5000/check_session", {
  credentials: "include",
});
```

For Axios, use:

```javascript
axios.defaults.withCredentials = true;
```

If the frontend runs on a different origin, set `FRONTEND_ORIGIN` to its exact origin (for example `http://localhost:3000`). The backend returns credentialed CORS headers only for that configured origin. Do not use wildcard origins with cookie authentication.

For production, serve the frontend and API over HTTPS, set a strong `SECRET_KEY`, and set `SESSION_COOKIE_SECURE=true`. A production deployment should also add CSRF protection and configure trusted origins deliberately.

## API endpoints

All request and response bodies use JSON unless a response is `204 No Content`.

| Method | Endpoint         | Authentication | Description                                      |
| ------ | ---------------- | -------------- | ------------------------------------------------ |
| POST   | `/signup`        | No             | Create an account; also logs the new user in     |
| POST   | `/login`         | No             | Verify credentials and create a session          |
| POST   | `/logout`        | No             | Clear the current session                        |
| GET    | `/check_session` | Session        | Return the currently authenticated user          |
| GET    | `/notes`         | Session        | Return only the current user's notes, paginated  |
| POST   | `/notes`         | Session        | Create a note owned by the current user          |
| GET    | `/notes/<id>`    | Session        | Retrieve one of the current user's notes         |
| PATCH  | `/notes/<id>`    | Session        | Partially update one of the current user's notes |
| DELETE | `/notes/<id>`    | Session        | Delete one of the current user's notes           |
| GET    | `/`              | No             | API information and endpoint overview            |

### Authentication request examples

Sign up:

```json
{ "username": "alice", "password": "password123" }
```

Log in:

```json
{ "username": "alice", "password": "password123" }
```

A successful signup returns `201`; login returns `200`. Both set a session cookie. Invalid credentials return `401`; a duplicate username returns `409`.

Logout is `POST /logout`. Checking the current session is `GET /check_session`; it returns `401` if no valid session exists.

### Notes request examples

Create a note:

```json
{ "title": "Project ideas", "content": "Plan the next release." }
```

Update part of a note:

```json
{ "title": "Updated title" }
```

List notes with pagination:

```text
GET /notes?page=1&per_page=10
```

The list response contains:

- `notes`: the current page of the authenticated user's notes.
- `pagination.page`, `pagination.per_page`, `pagination.total`, `pagination.pages`.
- `pagination.has_next` and `pagination.has_prev`.

`per_page` defaults to 10 and is capped at 100. Page numbers and page sizes must be positive integers.

### Authorization and status codes

- Unauthenticated access to protected routes returns `401`.
- A note that does not exist or belongs to another user returns `404`. This prevents the API from disclosing another user's record.
- Invalid JSON or field validation returns `400`.
- Successful creation returns `201`.
- Successful reads and updates return `200`.
- Successful deletion returns `204`.

## Run tests

```bash
pytest
```

The test suite covers password hashing, registration, duplicate usernames, login, session persistence, logout, protected routes, CRUD, pagination, and cross-user isolation.

## Project structure

```text
app.py                 Application factory and app setup
config.py              Configuration
extensions.py          SQLAlchemy, Bcrypt and Migrate instances
models/user.py         User model and password hashing
models/note.py         User-owned Note model
routes/auth.py         Signup, login, logout and session-check routes
routes/notes.py        Protected note CRUD and pagination
schemas/note_schema.py Note input validation
seed.py                Demo data creation
tests/                 Automated tests
```
