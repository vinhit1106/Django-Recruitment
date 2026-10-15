# Database setup and verification

## Local prerequisites

- Python 3.12 and the project `.venv`.
- PostgreSQL 17 (service `postgresql-x64-17` in the verified local environment).
- A database and user configured through `.env`; the checked environment uses database `recruitment` on `localhost:5432`.

## Configure

```powershell
Copy-Item .env.example .env
# Set DB_NAME, DB_USER, DB_PASSWORD, DJANGO_SECRET_KEY, and LAN origins in .env.
```

Never commit `.env` or put credentials in documentation.

## Migrate and verify

```powershell
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.venv\Scripts\python.exe manage.py migrate --noinput
.venv\Scripts\python.exe manage.py showmigrations
.venv\Scripts\python.exe manage.py migrate --plan
```

The verified local database is PostgreSQL (`connection.vendor=postgresql`, database `recruitment`). No migration operations remained pending during the Phase 9 audit.

## Seed local demo data

Use a local-only password supplied through the environment or command line:

```powershell
$env:DEMO_PASSWORD = "choose-a-local-password"
.venv\Scripts\python.exe manage.py seed_demo_data
```

The command is idempotent and does not delete existing records. It creates or updates a demo candidate, employer/company, Software Engineering category, published and pending jobs, and one candidate application. It must not be run automatically in production.

Demo emails are `demo.candidate@example.com` and `demo.employer@example.com`; the password is the value you provide at runtime and is never stored in the repository.
