# Integration gaps and follow-up risks

## Partial or blocked items

- Local `.env` is intentionally development-oriented (`DEBUG=True`). A production-like `manage.py check --deploy` run passed when a strong `DJANGO_SECRET_KEY`, `DEBUG=False`, HTTPS redirect, secure cookies and HSTS were supplied through environment variables.
- The local ignored `.env` key was rotated during JWT verification. Do not copy it to another environment; provision a separate strong secret and require users to log in again after key rotation.
- The supplied LAN addresses are configuration examples. Access from `192.168.1.110` was not observable from this host and must be verified manually.
- Antivirus/malware scanning for uploaded CVs is not implemented.
- Email notifications, background processing, and production object storage are outside the current local integration scope.
- No frontend repository was available for compatibility testing.

## Done with evidence

- PostgreSQL connection and live schema introspection.
- Migration consistency and no pending operations.
- Authentication, role ownership, recruitment workflows, admin moderation, dashboards, OpenAPI validation, seed idempotency, and local HTTP smoke coverage.
