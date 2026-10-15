# API integration

## Configuration

Use one Vite variable:

```env
VITE_API_BASE_URL=http://192.168.1.93:8000/api/v1
```

For a Backend running on the same computer, `http://localhost:8000/api/v1` is valid. Restart Vite after changing `.env`.

## Auth adapters

| Feature | Method | Path | Request | Status |
|---|---|---|---|---|
| Login | POST | `/auth/login/` | `{ email, password }` | Adapter implemented; response PENDING_VERIFICATION |
| Register | POST | `/auth/register/` | `{ email, password, first_name, last_name, role: CANDIDATE }` | Adapter implemented; response PENDING_VERIFICATION |
| Refresh | POST | `/auth/refresh/` | `{ refresh }` | Single-flight adapter; response PENDING_VERIFICATION |
| Logout | POST | `/auth/logout/` | `{ refresh }` + Bearer access | Adapter implemented; server response PENDING_VERIFICATION |
| Current user | GET | `/auth/me/` | Bearer access | AuthProvider adapter; response PENDING_VERIFICATION |

## Jobs adapters

| Feature | Method | Path | Status |
|---|---|---|---|
| Jobs list | GET | `/jobs/` | Query adapter implemented; response PENDING_VERIFICATION |
| Job detail | GET | `/jobs/{id}/` | Adapter implemented; response PENDING_VERIFICATION |

No Candidate, Employer, or Admin endpoint is implemented without a verified contract.
