# Frontend Architecture Audit

Updated: 2026-10-15

## Current structure

- `client/src/App.tsx` contains page/workspace implementations and mutation handlers; route composition now lives in `client/src/app/routes.tsx`. The remaining page extraction is incremental so current workflows stay stable.
- `client/src/api/client.ts` centralizes JSON/blob requests, JWT refresh, and structured API errors.
- `client/src/api/auth.ts`, `jobs.ts`, and `portal.ts` provide typed feature API boundaries.
- `client/src/auth/AuthProvider.tsx` owns session restoration, normalized roles, sign-in, sign-out, and transient network error handling.
- `client/src/styles/global.css` contains the shared visual tokens and responsive rules.

## Verified decisions

- Backend role values are `CANDIDATE`, `EMPLOYER`, and `ADMIN`; public registration accepts Candidate or Employer. Admin is provisioned outside public registration.
- Candidate skills are associations to an existing active global Skill. The UI now loads `/api/v1/candidate/skills/catalog/` and submits `skill_id`; it never creates or deletes global skills.
- Employer onboarding is supported by the existing registration endpoint and company create endpoint. The public CTA now opens `/register?role=EMPLOYER`.
- Protected data continues to use bearer-authenticated endpoints; frontend visibility does not replace backend authorization.

## Status

| Concern | Status | Evidence / next slice |
|---|---|---|
| Central API/auth handling | PASS | Existing client and AuthProvider; typecheck/build pass |
| Role-aware routing | PASS | ProtectedRoute and normalized role mapping; backend auth tests pass |
| Public jobs/companies | PASS | Real jobs and companies endpoints integrated |
| Candidate workflow | PASS | Profile, catalog-backed skills, experiences, CVs, applications integrated |
| Employer workflow | PASS | Employer registration CTA, company, jobs, applications integrated |
| Admin workflow | PARTIAL | Moderation and read-only users/categories integrated; management mutation controls remain |
| Component boundaries | PARTIAL | Route composition is extracted to `src/app/routes.tsx`; page/workspace modules remain the next safe extraction slice |
| UI feedback primitives | PASS | Shared `FieldErrors`, `Toast`, API error formatting and accessible roles are available in `components/feedback` |
| Browser E2E | NOT TESTED | Requires an actual browser session and test accounts |

## Safe follow-up refactor

The next structural slice should move one complete boundary at a time: first `ProtectedRoute` and dashboard pages, then public pages, then role workspaces. Each move must preserve the current API modules and run `npm exec tsc -- --noEmit` plus `npm run build` before continuing.
