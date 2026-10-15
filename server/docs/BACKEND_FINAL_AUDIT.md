# Backend final verification — PTIT CareerHub

Audit date: 2026-10-15 (Asia/Saigon)

This report records only checks rerun in the current workspace. Secrets and token values are intentionally omitted.

## JWT root cause and fix

The warning was caused by the local `DJANGO_SECRET_KEY` being shorter than the HMAC-SHA-256 minimum. SimpleJWT had no explicit signing key, so it implicitly reused Django's `SECRET_KEY`. No secret value was printed or committed.

The fix now requires `DJANGO_SECRET_KEY` at startup, rejects values below 32 bytes or with insufficient entropy, and explicitly configures SimpleJWT with `ALGORITHM=HS256`, `SIGNING_KEY=SECRET_KEY`, and an empty `VERIFYING_KEY`. The ignored local `.env` key was rotated. Any access or refresh token issued before that rotation is invalid and users must authenticate again.

## Final status matrix

| Area | Status | Evidence |
|---|---|---|
| Phase 2 bootstrap/settings/API prefix | VERIFIED | `manage.py check` passed; routes use `/api/v1/` |
| Phase 3 PostgreSQL models/schema/migrations | VERIFIED | Live connection reports PostgreSQL database `recruitment`; 22 tables introspected; no model drift; no pending plan |
| Phase 4 JWT authentication | VERIFIED | Full tests and live smoke cover register/login/me/refresh rotation/logout |
| Phase 5 candidate/profile/CV privacy | VERIFIED | Candidate test suite and full regression pass; CV access is ownership checked |
| Phase 6 company/jobs | VERIFIED | Company/jobs tests and live public jobs pagination smoke pass |
| Phase 7 applications/workflow | VERIFIED | Full regression covers duplicate prevention, ownership and transitions |
| Phase 8 admin/moderation/dashboards | VERIFIED | Full regression includes admin tests and scoped dashboards |
| Phase 9 local integration | VERIFIED | Seed idempotency, strict OpenAPI, PostgreSQL and HTTP smoke all rerun |
| LAN access from frontend host | BLOCKED / NOT TESTED | This environment cannot inspect the separate `192.168.1.110` host; IP/firewall queries were denied by OS permissions |
| Production deployment | PARTIAL | Production-like `check --deploy` passes with secure environment variables; actual HTTPS proxy/storage/host firewall not deployed here |

## PostgreSQL verification

The current Django connection reported:

- vendor: `postgresql`
- database: `recruitment`
- host: `localhost`
- 22 tables, including users, candidate domain, companies, jobs, applications, status history and JWT blacklist tables.
- Primary keys, foreign keys, unique constraints and domain indexes were returned by Django PostgreSQL introspection.

Commands rerun:

```text
.venv\Scripts\python.exe manage.py check                         PASS
.venv\Scripts\python.exe manage.py makemigrations --check --dry-run PASS
.venv\Scripts\python.exe manage.py showmigrations                all applied
.venv\Scripts\python.exe manage.py migrate --plan                no planned operations
```

No migration file was added in this audit because no model drift was found.

## Test and API evidence

- Full Django suite: **43 tests passed, 0 failed, 0 skipped** using the existing PostgreSQL test database with `--keepdb`.
- OpenAPI: `manage.py spectacular --validate --fail-on-warn --format openapi-json --file docs/openapi.json` passed with exit code 0.
- Django system check: passed with no issues.
- Production-like deployment check: passed with strong secret, `DEBUG=False`, HTTPS redirect, secure cookies and HSTS environment values.
- Seed command ran twice and returned the same demo IDs (`company_id=3`, `published_job_id=3`, `pending_job_id=4`, `application_id=3`), proving idempotent reuse in PostgreSQL.
- Direct PostgreSQL-backed count check after seeding returned 2 demo users, 1 demo company, 2 demo jobs and 1 demo application.
- HTTP smoke ran against a fresh local server on port `8012` after key rotation and passed health/database, live registration schema, Candidate/Employer registration, Candidate profile creation, duplicate/Admin/weak-password rejection, login, me, public jobs pagination, refresh rotation and logout.
- The five JWT security tests are included in the 43-test total and cover malformed/missing Bearer tokens, expired access tokens, old refresh rejection after rotation, logout blacklist behavior and CORS authorization preflight.

The smoke script stores tokens in memory and never prints passwords or token values.

## Contract and documentation fixes made during final verification

- Removed the weak development secret fallback. The application now fails fast when `DJANGO_SECRET_KEY` is missing or shorter than 32 bytes / too low entropy.
- Declared JWT settings explicitly: `HS256`, `SIGNING_KEY=SECRET_KEY`, `VERIFYING_KEY=""`, 30-minute access lifetime, 7-day refresh lifetime, rotation and blacklist-after-rotation.
- Rotated the local ignored `.env` key. Existing tokens signed with the previous key must be discarded and users must log in again.
- Corrected the registration success example in `docs/API_CONTRACT.md` so it shows `{user, access, refresh}` rather than request fields.
- Updated `.env.example` with the expected LAN backend/frontend origins while keeping values non-secret and environment-driven.
- Corrected ERD/deployment wording for private CV storage and authorized downloads.
- Added this final audit report.

## LAN checks

Verified from settings (with environment overrides, without printing secret values):

- `ALLOWED_HOSTS`: localhost, loopback and `192.168.1.93`.
- CORS and CSRF origins include localhost/loopback Vite origins and `http://192.168.1.110:5173`.
- No wildcard CORS setting is used.
- Backend can be started with `manage.py runserver 0.0.0.0:8000`.

Not verified here:

- HTTP request from the separate frontend machine.
- Windows firewall rule and actual interface address; administrative network queries were denied.

Manual check on the backend/ frontend machines:

```powershell
.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000
```

Then from the frontend machine open `http://192.168.1.93:8000/api/v1/health/` and confirm the response contains `{"status":"ok","database":"ok"}`. If unreachable, check the backend host IP and inbound TCP 8000 firewall rule.

## Not implemented / outside local scope

- Antivirus or malware scanning for uploaded CVs.
- Email notifications and background job processing.
- Production object storage and HTTPS reverse proxy deployment.
- Direct frontend repository compatibility tests; no frontend source was present in this workspace.

These are recorded as follow-up scope, not claimed as completed backend functionality.
