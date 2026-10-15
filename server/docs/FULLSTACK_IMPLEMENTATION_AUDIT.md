# PTIT CareerHub full-stack implementation audit

Audit date: 2026-10-15 (Asia/Saigon)

This audit is based on the source currently present in `server/` and `client/`. Statuses below describe inspected implementation and observed verification results; a feature is not marked PASS solely because documentation claims it exists.

| Module | Backend | Frontend | API integration | Tests | Conclusion |
|---|---|---|---|---|---|
| Authentication | PASS; JWT endpoints and rotation are implemented | PARTIAL; login/register and token refresh exist | PASS for client auth client; role session is now synchronized | Backend PASS; frontend browser pending | Foundation implemented |
| Public jobs | PASS; public filtering/pagination/detail endpoints | PASS; homepage, search, filters and detail use API when configured | PASS | Build PASS; browser pending | Implemented |
| Companies | PASS; public and employer company endpoints | PASS; public list/detail pages, job links and employer company form integrated | PASS | Build PASS; browser pending | Browser verification pending |
| Candidate profile | PASS; ownership-scoped profile endpoint | PASS; role protected dashboard includes profile update form | PASS | Backend PASS; frontend browser pending | Implemented in source |
| Skills/experiences | PASS; CRUD/ownership rules exist | PARTIAL; add/remove skills and experience CRUD UI integrated | PASS by source; browser pending | Partial | Skill catalog picker remains |
| CV management | PASS; PDF validation and private download endpoints exist | PASS; upload/download/delete UI integrated | PASS by source; browser pending | Partial | Browser verification pending |
| Applications | PASS; apply, list, detail and withdraw endpoints exist | PASS; apply/list/detail/withdraw integrated | PASS | Build PASS; browser pending | Browser verification pending |
| Employer company | PASS | PASS; create/update form integrated | PASS by source | Partial | Browser verification pending |
| Employer jobs | PASS; scoped CRUD and moderation submission | PASS; create/edit/close/submit integrated | PASS | Build PASS; browser pending | Browser verification pending |
| Employer applications | PASS; scoped review and status transitions | PASS; list/detail/transitions and protected CV download integrated | PASS | Build PASS; browser pending | Browser verification pending |
| Admin moderation | PASS; dashboard and moderation endpoints | PASS; pending list, detail, approve/reject and inline reason integrated | PASS | Build PASS; browser pending | Browser verification pending |
| Dashboards | PASS; candidate/employer/admin database counts | PASS; role-specific protected dashboards consume API | PASS | Backend PASS; frontend browser pending | Implemented in source |
| Notifications/feedback | OUT OF CURRENT API SCOPE | NOT IMPLEMENTED | N/A | NOT TESTED | External/remaining scope |
| Responsive/accessibility | N/A | PARTIAL; existing responsive CSS plus portal responsive states | N/A | NOT TESTED in browser | Browser verification pending |
| Security | PASS by backend audit/docs; ownership and JWT rules present | PARTIAL; bearer/refresh handling and role guards implemented | PASS by inspection | Backend tests PASS; browser pending | Runtime browser regression pending |
| Deployment/configuration | PARTIAL; backend docs and env examples exist | PASS for `VITE_API_BASE_URL` configuration | PARTIAL | Local server PASS; LAN not tested | LAN and production infra remain |

## Baseline evidence

- The repository includes a `.venv`, but its uv launcher points to an old removed Python home. The installed packages remain usable through the bundled Python 3.12 interpreter with `server/.venv/Lib/site-packages` on `PYTHONPATH`.
- With that interpreter and a writable temporary `DJANGO_MEDIA_ROOT`, backend checks, OpenAPI validation, migration drift and all 43 tests pass.
- Frontend `npm exec tsc -- --noEmit` and `npm run build` pass with the installed `node_modules` and Node 26.12.
- Backend server starts with `.venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000`; health and public jobs smoke requests return HTTP 200.
- Browser E2E and LAN-from-another-device remain NOT TESTED.

## Source changes in this implementation slice

- Centralized role normalization (`CANDIDATE`, `EMPLOYER`, `ADMIN`) and session restoration in `client/src/auth/AuthProvider.tsx`.
- Added typed portal API methods in `client/src/api/portal.ts` for dashboards, profile, applications, employer data and moderation.
- Added protected candidate, employer and admin dashboard routes with loading, error, empty and responsive states in `client/src/App.tsx`.
- Added portal layout styles and mobile rules in `client/src/styles/global.css`.
- Auth regression root cause: `refreshUser()` stored a normalized lowercase role in context but returned the raw uppercase role from `/auth/me/`; registration then compared `CANDIDATE` with `candidate` and navigated to the employer portal. All auth paths now validate and return the same normalized user shape.

