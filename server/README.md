# Django Recruitment Backend

PTIT CareerHub recruitment API built with Django, Django REST Framework, PostgreSQL, Simple JWT and drf-spectacular.

## Local setup

```powershell
uv venv .venv --python 3.12
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
Copy-Item .env.example .env
# Configure DB_* and a local DJANGO_SECRET_KEY in .env.
.venv\Scripts\python.exe manage.py migrate
```

Run locally or on the LAN:

```powershell
.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

The API base is `/api/v1/`; LAN health is `http://192.168.1.93:8000/api/v1/health/`. OpenAPI JSON is `/api/schema/` and Swagger UI is `/api/docs/`.

## Implemented backend scope

- Email-based Candidate, Employer and Admin accounts with JWT login, rotation and blacklist logout.
- Verified registration contract: `POST /api/v1/auth/register/` accepts `email`, `password`, optional names and optional `role` (`CANDIDATE` by default or `EMPLOYER`), and returns `{user, access, refresh}` with no password fields.
- Candidate profile, skills, experiences and private PDF CV upload/download.
- Employer-owned companies and jobs with moderation, public filtering and pagination.
- Candidate applications, employer review transitions, withdrawal and status history.
- Admin user/category management, job moderation and role-scoped dashboards.
- PostgreSQL constraints, indexes, migrations, OpenAPI schema and normalized API errors.
- Idempotent local `seed_demo_data` and a real HTTP smoke script.

## Demo data

```powershell
$env:DEMO_PASSWORD = "local-only-password"
.venv\Scripts\python.exe manage.py seed_demo_data
```

The command creates deterministic demo records without deleting existing data. Do not run it automatically in production.

## Validation

```powershell
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.venv\Scripts\python.exe manage.py spectacular --validate --file $env:TEMP\recruitment-openapi.yml
.venv\Scripts\python.exe manage.py test apps.adminapi apps.applications apps.accounts apps.candidates apps.companies apps.jobs --keepdb -v 1
$env:SMOKE_PASSWORD = "local-smoke-password"
.venv\Scripts\python.exe scripts/smoke_http.py
```

If `.venv\Scripts\python.exe` reports `uv trampoline failed` because the venv was moved with the project, use the bundled interpreter with the existing venv packages:

```powershell
$env:PYTHONPATH = "$PWD\.venv\Lib\site-packages"
$env:DJANGO_MEDIA_ROOT = "$env:TEMP\ptit-careerhub-media"
.uv-python\cpython-3.12.13-windows-x86_64-none\python.exe manage.py check
```

Use the same environment variables for tests. A writable media root is required by CV upload tests on restricted Windows workspaces.

See `docs/BACKEND_STATUS.md`, `docs/API_CONTRACT.md`, `docs/FRONTEND_INTEGRATION_GUIDE.md`, `docs/DATABASE_SETUP.md`, `docs/DATABASE_SCHEMA.md`, `docs/SMOKE_TESTS.md` and `docs/INTEGRATION_GAPS.md` for the verified handoff.
