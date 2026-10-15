# Frontend integration guide

## Base URL

Local backend: `http://127.0.0.1:8000`.
LAN example: `http://192.168.1.93:8000` when the backend host actually has that address. Confirm the address on the backend machine before sharing it.

API prefix: `/api/v1/`.

## Authentication

1. `POST /api/v1/auth/register/` with JSON `{email,password,first_name?,last_name?,role?}`. `role` defaults to `CANDIDATE`; use `EMPLOYER` for employer accounts. Do not send `ADMIN`.
2. `POST /api/v1/auth/login/` with `{email,password}`.
3. Send the returned access token as `Authorization: Bearer <access>`.
4. Send refresh tokens only in JSON to `POST /api/v1/auth/refresh/`; rotation is enabled.
5. Revoke the current refresh token with authenticated `POST /api/v1/auth/logout/`.

Registration returns HTTP 201 with `{user, access, refresh}`. The `user` object contains `id`, `email`, `first_name`, `last_name`, `role`, and `created_at`; it never contains a password. Validation failures return HTTP 400 with `error.code=VALIDATION_ERROR` and field details, for example `error.details.email` or `error.details.password`.

Keep access and refresh tokens out of URLs and logs. Handle `401` by attempting one refresh, then redirecting to login if refresh fails.

The backend uses `HS256` JWTs with Bearer access headers. Refresh rotation is enabled: after a successful refresh, replace the stored refresh token with the returned one and discard the old token. Logout blacklists the submitted refresh token; it does not retroactively revoke an already issued access token, which remains valid until expiry.

## Response conventions

Paginated lists return `count`, `next`, `previous`, and `results`. Handled errors return `error.code`, `error.message`, and `error.details`. Public jobs are only published and non-expired jobs.

## Main routes

- Candidate: `/candidate/profile/`, `/candidate/skills/`, `/candidate/experiences/`, `/candidate/cvs/`, `/candidate/applications/`.
- Employer: `/employer/company/`, `/employer/jobs/`, `/employer/applications/`, `/employer/dashboard/`.
- Public: `/companies/`, `/jobs/`, `/api/v1/health/`.
- Admin: `/admin/users/`, `/admin/categories/`, `/admin/jobs/pending/`, `/admin/jobs/{id}/approve/`, `/admin/jobs/{id}/reject/`, `/admin/dashboard/`.

The complete method and field matrix is in `docs/API_CONTRACT.md`; the generated schema is available at `/api/schema/` and Swagger UI at `/api/docs/`.

## CV upload/download

Upload `multipart/form-data` with `file`; only PDF files up to 5 MiB whose content starts with `%PDF-` are accepted. CV metadata endpoints never expose a public URL. Candidate downloads are owner-only; employer downloads require an application on a job owned by that employer.

## CORS/LAN

Set `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` to the actual frontend origin, such as `http://192.168.1.110:5173`, in the backend `.env`. Do not use wildcard origins for this API.
