# PTIT CareerHub Feature Gap Matrix

Updated: 2026-10-15

Status meanings: `PASS` is implemented and verified by source/build or backend tests; `PARTIAL` is usable but has a documented limitation; `NOT TESTED` means browser or multi-device verification has not been run.

| Area | Backend contract | Frontend coverage | Status | Verification / remaining gap |
|---|---|---|---|---|
| Auth | `/auth/register/`, `/auth/login/`, `/auth/me/`, `/auth/refresh/`, `/auth/logout/` | AuthProvider, login/register, role guards and session recovery | PASS | TypeScript/build and HTTP smoke pass; browser matrix NOT TESTED |
| Public jobs | `GET /jobs/`, `GET /jobs/{id}/` with search, location, category, employment type, salary and ordering | Home, listing, detail and query filters | PASS | Build pass; browser NOT TESTED |
| Public companies | `GET /companies/`, `GET /companies/{id}/` | Company list/detail pages and job links | PASS | Build pass; browser NOT TESTED |
| Candidate profile | `GET/PATCH /candidate/profile/` | Dashboard profile form | PASS | Backend suite pass; browser NOT TESTED |
| Candidate skills | `GET /candidate/skills/catalog/`; `GET/POST /candidate/skills/`, `DELETE /candidate/skills/{id}/` | Active catalog picker, add/remove association | PASS | Backend catalog endpoint and regression test pass |
| Candidate experiences | `GET/POST /candidate/experiences/`, `PATCH/DELETE /candidate/experiences/{id}/` | Create/delete experience UI | PARTIAL | Edit control and browser validation remain |
| Candidate CVs | `GET/POST /candidate/cvs/`, `DELETE`, private download | PDF upload/list/download/delete | PASS | Backend and build pass; browser NOT TESTED |
| Candidate applications | list/create/detail/withdraw endpoints | Apply from job detail, list, detail route, withdraw | PASS | Build pass; duplicate/closed-job behavior delegated to backend |
| Employer company | `GET/POST/PATCH /employer/company/` | Create/update form | PASS | Backend suite pass; browser NOT TESTED |
| Employer jobs | list/create/detail PATCH/DELETE, submit and close actions | Create, edit, submit, close and status display | PASS | Build pass; browser NOT TESTED |
| Employer applications | list/detail, transition and protected CV download | List, detail, status transition and download | PASS | Build pass; browser NOT TESTED |
| Admin moderation | pending list/detail, approve/reject | Pending jobs, inline rejection reason, approve/reject | PASS | Build pass; browser NOT TESTED |
| Admin users/categories | list/detail update and category CRUD | Read-only user/category panels | PARTIAL | Listing is integrated; update/create/delete controls remain |
| Dashboards | candidate/employer/admin dashboard endpoints | Role-specific metrics and recent activity | PASS | Backend suite pass; browser NOT TESTED |
| Error/feedback UX | Structured DRF field errors | Shared field errors, toast primitive, readable auth errors and mutation loading | PASS | Build pass; browser visual verification NOT TESTED |
| Browser/LAN | N/A | N/A | NOT TESTED | Requires a real browser session and second-device/LAN environment |

## Environment evidence

- Recreated `server/.venv` is a standard Python 3.12 environment; the previous uv trampoline is retained as `.venv-uv-broken` for recovery reference.
- Backend system checks, migration drift, OpenAPI validation and the existing 43-test suite pass with a writable temporary media root.
- Frontend `npm exec tsc -- --noEmit`, `npm run build` and `git diff --check` pass.
