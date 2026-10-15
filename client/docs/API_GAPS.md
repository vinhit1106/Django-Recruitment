# API gaps

1. `docs/FRONTEND_INTEGRATION_GUIDE.md`, `docs/API_CONTRACT.md`, `docs/openapi.json`, `docs/BACKEND_FINAL_AUDIT.md`, and `docs/SMOKE_TESTS.md` are absent from this frontend repository.
2. Backend connectivity is not verified from this environment. A browser error such as `ERR_CONNECTION_REFUSED` means no process is listening at the configured host/port; it is not evidence of a frontend auth failure.
3. The frontend accepts `access_token`/`refresh_token` aliases defensively, but the expected contract in the supplied prompt uses `access`/`refresh`; this must be confirmed against OpenAPI.
4. Register currently sends `first_name`, `last_name`, and fixed `role: CANDIDATE`; employer registration UI is not yet exposed because its exact required fields are not verified.
5. Auth state is restored through `/auth/me/` when a token exists. Network errors are surfaced and do not silently become local login success.
6. LocalStorage token persistence is a documented client-side XSS risk; no claim is made that it protects JWTs from XSS.
7. Candidate profile, skills, experience, CV, applications, Employer, Admin, companies, health check, protected routes, and role dashboards remain pending the backend contract.

When Backend is available: set `VITE_API_BASE_URL`, restart Vite, allow the actual frontend origin in Django CORS, inspect Network responses for auth/jobs, then replace the pending labels with confirmed serializer-derived types.
