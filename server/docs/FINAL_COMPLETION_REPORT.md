# Final Completion Report

PTIT CareerHub is a Django REST Framework and React TypeScript recruitment portal with Candidate, Employer, Admin and public workflows.

## Delivered

- JWT authentication with refresh and expired-session handling.
- Candidate profile, skills, experiences, private CVs and applications.
- Employer company and job lifecycle: draft, submit, moderation and close.
- Public job/company pages with API-backed category filtering and pagination.
- Admin dashboard, users, categories, skills and job moderation APIs/UI.
- Idempotent reference/demo data seeding through `seed_demo_data`.

## Run

```powershell
cd server
python manage.py migrate
$env:DEMO_PASSWORD = "local-development-password"
python manage.py seed_demo_data
python manage.py runserver 127.0.0.1:8000

cd ..\client
npm install
npm run dev
```

The frontend reads `VITE_API_BASE_URL` from `client/.env`.

## Validation

System checks, migration consistency, focused backend suites, TypeScript and the production frontend build pass. The full suite may require the local PostgreSQL test database to be recreated and the media directory to be writable.
