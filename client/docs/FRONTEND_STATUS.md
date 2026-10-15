# Frontend status

Updated: 2026-10-15

## CONFIRMED in this repository

- React + TypeScript + Vite production build succeeds.
- Canonical API configuration is `VITE_API_BASE_URL`; the current local `.env` points to `http://localhost:8000/api/v1`.
- API client normalizes one leading slash and does not append another API prefix.
- Login sends JSON `{ email, password }` to `/auth/login/`.
- Register sends JSON `{ email, password, first_name, last_name, role: "CANDIDATE" }` to `/auth/register/`; the UI does not expose ADMIN registration.
- Bearer access token is centralized; refresh is single-flight and only retries the original GET once.
- API-configured screens no longer replace API errors with local demo data.
- Local demo data is only shown when the API base URL is absent and is visibly labeled.
- AuthProvider verifies an existing session through `/auth/me/` during reload and clears invalid local tokens.

## ASSUMED

- Auth responses contain `access` and `refresh` (aliases are accepted only for compatibility).
- Register accepts the fields described by the supplied mega prompt.
- Jobs use DRF pagination with `results`.
- Browser-accessible localStorage is acceptable for the current JWT architecture; this carries XSS risk and should be replaced by an HttpOnly-cookie design if Backend supports it.

## PENDING_VERIFICATION / BLOCKED

- No Backend source or OpenAPI files are present in this repository.
- LAN/localhost HTTP verification is blocked when Django is not running or not reachable from this environment.
- Exact serializer field names, CORS origins, health endpoint, role-specific endpoints, candidate/employer/admin flows, and CV/application schemas remain unverified.

## Latest check

- `npm run build`: PASS.
- LAN browser verification: BLOCKED / NOT VERIFIED.
