# API contract (implemented)

This document describes the implemented Phase 2–9 API. The authoritative machine-readable contract is generated at `/api/schema/` and validated with `manage.py spectacular --validate`.

## Base URL and conventions

- Base path: `/api/v1/`
- JSON fields use `snake_case`.
- List responses use `{ "count": 0, "next": null, "previous": null, "results": [] }`.
- Errors use `{ "error": { "code": "...", "message": "...", "details": {} } }`.

## Required endpoint groups

Authentication endpoints:

| Method | Path | Auth | Behavior |
|---|---|---|---|
| POST | `/auth/register/` | Guest | Creates Candidate by default, or Employer when `role=EMPLOYER`; never creates Admin. Returns user plus access and refresh JWTs. |
| POST | `/auth/login/` | Guest | Accepts `email` and `password`; returns user plus access and refresh JWTs. |
| POST | `/auth/refresh/` | Guest | Accepts a refresh JWT and returns a new access JWT. Rotation is enabled; the submitted refresh token is blacklisted. |
| POST | `/auth/logout/` | Authenticated | Accepts the current refresh JWT and blacklists it. Returns `204`. |
| GET | `/auth/me/` | Authenticated | Returns the authenticated user. |

JWTs are sent in the `Authorization: Bearer <access_token>` header. Refresh tokens are sent in JSON request bodies, never URLs. Phase 4 uses Simple JWT's database blacklist for revocation; refresh rotation and blacklist-after-rotation are enabled.

JWT signing uses `HS256` with the environment-managed `DJANGO_SECRET_KEY`; the key is never returned or logged. Access tokens expire after 30 minutes by default and refresh tokens after 7 days. Replacing the signing key invalidates previously issued tokens, so clients must authenticate again after a key rotation.

### Registration contract (verified against live OpenAPI and HTTP)

`POST /api/v1/auth/register/` is public and accepts JSON only for the documented contract:

```json
{
  "email": "candidate@example.com",
  "password": "A-strong-password-123",
  "first_name": "An",
  "last_name": "Nguyen",
  "role": "CANDIDATE"
}
```

Required fields are `email` and `password`. `first_name` and `last_name` are optional strings. `role` is optional and defaults to `CANDIDATE`; the only accepted values are `CANDIDATE` and `EMPLOYER`. `ADMIN` is intentionally absent from the request schema and is rejected by the API. Email is normalized to lowercase and duplicate emails return HTTP 400 with `error.details.email`. Password policy requires at least 8 characters and rejects common or entirely numeric passwords; it does not reject a password merely because it resembles the email address.

The successful HTTP 201 response is:

```json
{"user":{"id":1,"email":"candidate@example.com","first_name":"An","last_name":"Candidate","role":"CANDIDATE","created_at":"2026-10-14T10:00:00+07:00"},"access":"<jwt>","refresh":"<jwt>"}
```

Candidate registration creates `/candidate/profile/` in the same database transaction. Employer registration does not create a candidate profile. Passwords, privilege flags and token values are never returned in the `user` object.

Refresh and logout requests use `{"refresh":"<jwt>"}`. Admin registration is rejected with HTTP 400 and `VALIDATION_ERROR`.

Health: `GET /health/` is public and returns `{ "status": "ok", "database": "ok" | "unavailable" }`.

Candidate: `/candidate/profile/`, `/candidate/skills/`, `/candidate/experiences/`, `/candidate/cvs/`, `/candidate/applications/`.

Phase 5 candidate endpoints:

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET/PATCH | `/candidate/profile/` | Candidate | Accesses only the profile belonging to the JWT user. System fields are read-only. |
| GET/POST | `/candidate/skills/` | Candidate | Lists or adds a shared active Skill association using `skill_id`. |
| DELETE | `/candidate/skills/{id}/` | Candidate | Deletes only the current candidate's association. |
| GET/POST | `/candidate/experiences/` | Candidate | Creates/list experiences owned by the current candidate. |
| GET/PATCH/DELETE | `/candidate/experiences/{id}/` | Candidate | Queryset is ownership-scoped. `is_current=true` clears `end_date`. |
| GET/POST | `/candidate/cvs/` | Candidate | Multipart PDF upload/list. Maximum 5 MB; file signature must start with `%PDF-`. |
| GET/PATCH/DELETE | `/candidate/cvs/{id}/` | Candidate | Metadata/detail and owner-only delete. A CV referenced by an application cannot be deleted. |
| GET | `/candidate/cvs/{id}/download/` | Candidate | Owner-only private download with `application/pdf` and attachment disposition. |

CV list/detail responses expose metadata only; they do not expose a public file URL or filesystem path. Upload uses `multipart/form-data` with the `file` field. The stored filename is UUID-based and the original filename is metadata only.

Candidate profile is created explicitly when a Candidate registers. A Candidate created through another administrative path without a profile receives `PROFILE_NOT_FOUND` until the profile is provisioned.

Company and jobs:

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET/POST/PATCH | `/employer/company/` | Employer | One Company per Employer; owner is always taken from JWT. POST returns `409 COMPANY_EXISTS` on duplicate. |
| GET | `/companies/` | Public | Paginated public company metadata. |
| GET | `/companies/{id}/` | Public | Public fields only; owner email and internal fields are excluded. |
| GET | `/jobs/` | Public | Only `PUBLISHED` jobs with `deadline >= today`. Supports `search`, `location`, `category`, `employment_type`, `salary_min`, `salary_max`, `ordering`, `page`, `page_size`. |
| GET | `/jobs/{id}/` | Public | Same public visibility rule as list. Draft, pending, rejected, closed and expired jobs return 404. |
| GET/POST | `/employer/jobs/` | Employer | Scoped to the Employer's Company. POST always creates `DRAFT`; `company_id`, owner and status are ignored/read-only. |
| GET/PATCH/DELETE | `/employer/jobs/{id}/` | Employer | Ownership-scoped CRUD. |
| POST | `/employer/jobs/{id}/submit/` | Employer | `DRAFT` or `REJECTED` -> `PENDING`. |
| POST | `/employer/jobs/{id}/close/` | Employer | Transitions an owned job to `CLOSED`. |

Job fields accepted on Employer create/update include `title`, `description`, `requirements`, `benefits`, `location`, `employment_type`, `salary_min`, `salary_max`, `salary_currency`, `deadline`, and active `category_id`. Deadline cannot be in the past and `salary_min <= salary_max`.

Public job responses include company and category public metadata, never owner identity or review internals.

Applications:

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET/POST | `/candidate/applications/` | Candidate | Lists the current candidate's applications, or applies with `job_id`, `cv_id`, and optional `cover_letter`. |
| GET | `/candidate/applications/{id}/` | Candidate | Ownership-scoped application detail. |
| POST | `/candidate/applications/{id}/withdraw/` | Candidate | Withdraws only `SUBMITTED`, `REVIEWING`, or `SHORTLISTED` applications. |
| GET | `/employer/applications/` | Employer | Lists applications belonging to the Employer's Company; supports `status` and `job_id` filters. |
| GET | `/employer/applications/{id}/` | Employer | Ownership-scoped detail. |
| POST | `/employer/applications/{id}/transition/` | Employer | Accepts `{ "status": "...", "note": "..." }`; only permitted transitions are accepted. |
| GET | `/employer/applications/{id}/cv/download/` | Employer | Private CV download only after application-to-owned-Job authorization. |

Apply request example:

```json
{"job_id":12,"cv_id":5,"cover_letter":"I am interested in this role."}
```

Application statuses are `SUBMITTED`, `REVIEWING`, `SHORTLISTED`, `REJECTED`, `HIRED`, and `WITHDRAWN`. Employer transitions are `SUBMITTED -> REVIEWING|REJECTED`, `REVIEWING -> SHORTLISTED|REJECTED`, and `SHORTLISTED -> HIRED|REJECTED`. Candidate withdrawal is allowed from `SUBMITTED`, `REVIEWING`, and `SHORTLISTED`, and leads to `WITHDRAWN`. `REJECTED`, `HIRED`, and `WITHDRAWN` are terminal.

The database unique constraint `(job_id, candidate_id)` prevents duplicate applications. Invalid eligibility (non-published or expired Job), another candidate's CV, or a duplicate submission returns a structured validation/conflict error. Application creation and every transition write `ApplicationStatusHistory` in one transaction.

Candidate CV APIs remain owner-only. Employer CV access is available solely through `/employer/applications/{id}/cv/download/` after the Application's Job is scoped to the Employer's Company.

Administration and dashboards:

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/admin/users/` | Admin | Paginated users; optional `role` and `is_active` filters. Passwords/tokens are never returned. |
| GET/PATCH | `/admin/users/{id}/` | Admin | Updates only `first_name`, `last_name`, and `is_active`; role/email/staff flags are read-only. The last active Admin cannot be disabled. |
| GET/POST | `/admin/categories/` | Admin | Category list/create with unique name and slug validation. |
| GET/PATCH/DELETE | `/admin/categories/{id}/` | Admin | Delete is blocked when a Job references the Category. |
| GET | `/admin/jobs/pending/` | Admin | Lists pending jobs for moderation. |
| GET | `/admin/jobs/pending/{id}/` | Admin | Pending job detail. |
| POST | `/admin/jobs/{id}/approve/` | Admin | `PENDING -> PUBLISHED`, records reviewer/time and `published_at`. |
| POST | `/admin/jobs/{id}/reject/` | Admin | `PENDING -> REJECTED`, requires `{ "reason": "..." }`. |
| GET | `/dashboard/candidate/` | Candidate | Counts and recent applications scoped to current Candidate. |
| GET | `/employer/dashboard/` | Employer | Job/application counts scoped to current Employer Company. |
| GET | `/dashboard/admin/` or `/admin/dashboard/` | Admin | Database totals by role, job status, application status and pending jobs. |

Dashboard response keys are stable: Candidate returns `application_count`, `applications_by_status`, `recent_applications`; Employer returns `company_id`, `job_count`, `jobs_by_status`, `application_count`, `applications_by_status`, `recent_applications`; Admin returns `user_count`, `users_by_role`, `company_count`, `job_count`, `jobs_by_status`, `pending_job_count`, `application_count`, and `applications_by_status`.

Administration: `/admin/users/`, `/admin/categories/`, `/admin/jobs/pending/`, `/admin/jobs/{id}/approve/`, `/admin/jobs/{id}/reject/`, `/admin/dashboard/`.

## Integration notes and gaps

- Frontend token storage remains a client decision; the backend contract is fixed to Authorization access headers and JSON refresh tokens.
- LAN addresses are deployment examples and must be checked on the actual hosts.
- Private object storage and malware/antivirus scanning are not included in this local integration scope.

The generated schema is also committed as `docs/openapi.json` and can be regenerated with `manage.py spectacular --validate --fail-on-warn --format openapi-json --file docs/openapi.json`.
