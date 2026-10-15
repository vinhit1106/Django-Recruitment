# Deployment notes (Phase 2)

- Set a strong `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, and explicit `DJANGO_ALLOWED_HOSTS`.
- Use PostgreSQL credentials supplied through the deployment environment, never source control.
- Serve the application over HTTPS and enable secure cookies/redirect settings at the production edge.
- Set `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` to the actual frontend origins only.
- Run `manage.py migrate` and `manage.py collectstatic` during deployment.
- Store uploaded CV files privately. CV downloads are served through authorization-checked API endpoints; do not expose `MEDIA_ROOT` as a public directory.
