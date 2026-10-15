# Smoke tests

## Automated HTTP smoke

Start the local development server (LAN use requires `0.0.0.0:8000`):

```powershell
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
$env:SMOKE_PASSWORD = "local-smoke-password"
.venv\Scripts\python.exe scripts/smoke_http.py
```

The script checks health and database availability, the live OpenAPI registration request/response schema, Candidate and Employer registration, candidate profile creation, duplicate/Admin/weak-password rejection, login, authenticated profile access, public job pagination, refresh rotation, and logout. It stores tokens only in memory and never prints them.

The dedicated JWT verification tests also cover malformed/missing Bearer headers, expired access tokens, reuse of an old rotated refresh token, refresh after logout, and a configured-origin preflight with the `authorization` header.

## Verified result

On 2026-10-14, the script passed against the local development server on port 8010. This proves local HTTP wiring only; LAN access from a separate frontend machine remains a manual check.
