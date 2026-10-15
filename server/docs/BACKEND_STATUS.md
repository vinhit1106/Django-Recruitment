# Backend status — Phase 9 local integration audit

Audit date: 2026-10-14 (Asia/Ho_Chi_Minh)

## Phase matrix

| Phase | Scope | Status | Evidence |
|---|---|---|---|
| 2 | Django/DRF/PostgreSQL bootstrap, settings, API prefix | DONE | `manage.py check`; live PostgreSQL connection |
| 3 | Domain models, constraints, migrations | DONE | PostgreSQL introspection; `makemigrations --check`; `migrate --plan` |
| 4 | JWT auth, refresh rotation/blacklist, current user | DONE | Auth tests and HTTP smoke |
| 5 | Candidate profile, skills, experiences, private CV | DONE | Candidate tests; ownership and PDF validation tests |
| 6 | Company and Jobs API | DONE | Company/Jobs tests; OpenAPI validation |
| 7 | Applications and status history/workflow | DONE | Application tests; transaction/history assertions |
| 8 | Admin moderation, user/category management, dashboards | DONE | Admin tests and scoped dashboard assertions |
| 9 | Database audit, seed, HTTP smoke, docs, configuration review | DONE locally / PARTIAL for LAN and production | Evidence below |

## Verified quality gates

- `manage.py check`: pass, no issues.
- `manage.py makemigrations --check --dry-run`: pass, no changes detected.
- `manage.py migrate --noinput`: pass, no migrations pending.
- `manage.py showmigrations`: all listed migrations applied.
- `manage.py migrate --plan`: no planned operations.
- `manage.py spectacular --validate --file ...`: pass, no schema warnings/errors.
- Full regression: **43 tests passed**, PostgreSQL test database reused with `--keepdb`; includes five JWT security/CORS tests.
- HTTP smoke: pass against local development server for health/database, live registration OpenAPI contract, Candidate/Employer registration, candidate profile creation, validation rejection, login, me, jobs pagination, refresh rotation, and logout.
- Seed command: two consecutive runs pass and reuse the same deterministic demo records.
- Production-like `manage.py check --deploy`: pass with a strong environment secret, `DEBUG=False`, HTTPS redirect, secure cookies and HSTS settings enabled.
- Registration schema: verified required fields, role enum, 201 response shape and runtime behavior; generated schema is stored in `docs/openapi.json`.
- JWT signing: explicit `HS256` with environment-managed `DJANGO_SECRET_KEY`; missing or weak keys fail fast.

## PostgreSQL evidence

The configured connection is PostgreSQL database `recruitment` on `localhost:5432`. Introspection confirmed the accounts, candidates, companies, jobs, applications, status-history, Django auth/admin/session and Simple JWT blacklist tables. Primary keys, foreign keys, unique constraints and domain indexes are present; no orphan or migration drift check failed.

## Files added or updated in Phase 9

- `apps/core/management/commands/seed_demo_data.py`
- `scripts/smoke_http.py`
- `docs/DATABASE_SCHEMA.md`
- `docs/DATABASE_SETUP.md`
- `docs/FRONTEND_INTEGRATION_GUIDE.md`
- `docs/SMOKE_TESTS.md`
- `docs/INTEGRATION_GAPS.md`
- `docs/BACKEND_FINAL_AUDIT.md`
- `.env.example`, `config/settings.py`, `README.md`, `docs/API_CONTRACT.md`, `docs/ERD.md`

## Security/configuration review

- Secrets remain environment-only; `.env` is ignored.
- Production mode now requires a non-empty high-entropy `DJANGO_SECRET_KEY`.
- Upload memory limits are configurable and aligned with the CV limit.
- CORS/CSRF origins are environment-driven and should contain only actual frontend origins.
- CV files remain private through application endpoints; media must not be exposed as a public directory.

## Remaining partial or blocked items

- `check --deploy` reports development/deployment warnings when the local `.env` uses `DEBUG=True` and a placeholder secret. Configure a strong secret, `DEBUG=False`, HTTPS redirect, secure cookies and HSTS for deployment.
- LAN reachability from frontend host `192.168.1.110` was not observable here; verify manually with backend bound to `0.0.0.0:8000` and the actual host firewall/network.
- Antivirus scanning, email notifications, background jobs and production object storage are not implemented.
- No frontend source was available for contract compatibility testing.

## Local commands

```powershell
.venv\Scripts\python.exe manage.py migrate
$env:DEMO_PASSWORD = "local-only-password"
.venv\Scripts\python.exe manage.py seed_demo_data
.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

Demo users are `demo.candidate@example.com` and `demo.employer@example.com`; their password is supplied at seed time and is not stored in source control.
