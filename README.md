# TaskHub technology test

TaskHub is a deliberately small Django application for learning how a modular monolith can combine Django Templates, HTMX, PostgreSQL, Supabase Storage, and Django Ninja. It is a technology test project, not a production-ready task manager.

## What it tests

- Django models, forms, views, templates, ORM, admin, and tests
- HTMX partial responses for create, complete, delete, filtering, and search
- PostgreSQL configuration compatible with local PostgreSQL or Supabase PostgreSQL
- Optional file uploads to Supabase Storage
- A small validated Django Ninja API
- GitHub Actions checks and tests

## Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `DJANGO_SECRET_KEY` and the `DB_*` values in `.env`. Setting `DB_NAME` activates PostgreSQL:

```text
DB_NAME=taskhub
DB_USER=postgres
DB_PASSWORD=your-local-password
DB_HOST=localhost
DB_PORT=5432
```

The database variables also work with the host, port, database name, user, and password supplied by Supabase. With `DB_NAME` empty, the project uses SQLite as a temporary learning fallback.

## Supabase Storage

Create a bucket such as `task-attachments`, then set these variables in `.env`:

```text
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-server-side-key
SUPABASE_BUCKET=task-attachments
SUPABASE_PUBLIC_URL=https://your-project.supabase.co/storage/v1/object/public/task-attachments
```

When these variables are missing, attachments are saved to local `media/attachments/` storage so the feature still works with SQLite. When they are present, uploads go to Supabase Storage. Never commit `.env`, Supabase keys, or local media files.

## Run

```powershell
python manage.py migrate
python manage.py createsuperuser  # optional
python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the introduction page, then choose **Enter TaskHub** to open the working task board at `/app/`. The API is available at `/api/tasks` and `/api/tasks/{id}`.

## Tests

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

The GitHub Actions workflow runs these checks on pushes and pull requests. It uses Django's default SQLite test database so CI does not need secrets or a hosted database.

## HTMX request map

- Create: `POST /tasks/create/` returns one task-card partial; `hx-target="#task-list"` and `hx-swap="afterbegin"` insert it.
- Complete: `POST /tasks/{id}/toggle/` returns the updated card; `hx-target="closest article"` and `hx-swap="outerHTML"` replace it.
- Delete: `DELETE /tasks/{id}/delete/` returns an empty response; the same target/swap removes the card.
- Filter/search: `GET /tasks/partial/` returns all matching cards; `hx-target="#task-list"` and `hx-swap="innerHTML"` replace the list contents.

## GitHub

```powershell
git init
git add .
git commit -m "Build TaskHub technology test"
git branch -M main
git remote add origin https://github.com/YOUR-USER/YOUR-REPO.git
git push -u origin main
```

Review `.gitignore` before pushing. Credentials, `.env`, and local SQLite files are excluded.
