# PTIT CareerHub full-stack completion report

## Executive summary

The repository contains a relatively complete Django recruitment API and a smaller React/Vite client. This implementation slice aligned the client authentication lifecycle with the backend role contract and added real API-backed candidate, employer and admin dashboard routes. Public jobs and authentication remain available through the existing pages.

The main local quality gates now run successfully. Remaining gaps are limited to browser E2E coverage and a few secondary management screens.

## Architecture

- Backend: Django REST Framework with PostgreSQL, Simple JWT rotation/blacklist, role and ownership permissions.
- Frontend: React + TypeScript + Vite, centralized `request()` client, local token storage, role-aware route guards.
- Contract: `/api/v1/`, snake_case JSON, paginated `{count,next,previous,results}` lists and normalized error objects.

## Completed in this slice

- Session restoration calls `/auth/me/` and clears invalid sessions.
- Login now updates the auth context and routes by backend role.
- Registration with returned tokens restores the current user before routing.
- Concurrent GET 401 refresh coordination remains centralized in the API client.
- Candidate, employer and admin routes call their real dashboard endpoints.
- Candidate profile editing calls `PATCH /candidate/profile/`.
- Candidate and employer application lists render API data with empty/error states.
- Candidate CV upload/download/delete, skills add/remove, experiences create/delete and real application submission are integrated with protected API endpoints.
- Employer company create/update, job draft creation/submission and application status transitions are integrated.
- Admin pending-job approve/reject actions are integrated.
- Protected routes redirect guests to login and mismatched roles to access denied.
- The broken uv-based `.venv` launcher was replaced with a standard Python 3.12 venv while preserving the installed packages; `.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000` now starts successfully.
- Fixed the registration redirect bug: backend returns `user.role = CANDIDATE`, while the previous frontend handler used the unnormalized `/auth/me/` return value (`CANDIDATE`) against lowercase route checks and fell through to the employer route. Login, registration and session restore now share one validated role normalization path.

## Remaining work

- Candidate application detail/withdraw UI and skill picker sourced from a public skills catalog remain.
- Employer full job edit/close UI and employer CV download UI remain.
- Admin users and categories management UI remain.
- Browser responsive/accessibility verification and full E2E workflows.
- LAN verification, production deployment and external services such as email, scanning and object storage.

## Test results

| Check | Status | Evidence |
|---|---|---|
| Django system check | PASS | Bundled Python + venv site-packages; no issues |
| Django test suite | PASS | 43 tests passed with writable temporary media root |
| Migration check | PASS | `makemigrations --check --dry-run`; no changes detected |
| OpenAPI validation | PASS | `manage.py spectacular --validate`; no warnings/errors |
| Frontend typecheck/build | PASS | `npm exec tsc -- --noEmit` and `npm run build` pass with installed `node_modules` |
| Browser E2E | NOT TESTED | Browser automation was not run in this environment |
| LAN verification | NOT TESTED | Requires actual network host and running servers |

## Run instructions

Backend: from `server/`, install `requirements.txt`, configure `.env`, run migrations, then `python manage.py runserver 0.0.0.0:8000`.

Frontend: from `client/`, use Node 20.19+ (or Node 22.12+), run `npm ci`, copy `.env.example` to `.env`, set `VITE_API_BASE_URL`, then run `npm run dev`.

## Acceptance matrix

| Criterion | Status | Evidence |
|---|---|---|
| Frontend build | PASS | Vite production build completed |
| Backend tests | PASS | 43 tests passed using bundled Python with existing venv packages |
| API contract | PASS by source/docs | Existing API contract and typed endpoint paths |
| JWT login/refresh/logout | PASS by source/docs; HTTP runtime smoke partial | Centralized client and backend contract |
| Candidate workflow | PARTIAL | Dashboard/profile/CV/skills/experience/apply UI integrated; browser E2E pending |
| Employer workflow | PARTIAL | Company/job create-submit/application review UI integrated; browser E2E pending |
| Admin workflow | PARTIAL | Dashboard and moderation UI integrated; user/category UI remains |
| PostgreSQL integrity | PASS | Existing backend audit plus passing PostgreSQL-backed tests |
| Responsive UI | PARTIAL | CSS rules added; browser verification pending |
| Security checks | PARTIAL | Backend audit evidence plus client guards; runtime rerun pending |
| LAN browser test | NOT TESTED | External network verification required |
| Documentation | PASS | API/integration docs plus this report |

