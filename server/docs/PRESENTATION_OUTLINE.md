# Presentation Outline

1. **Problem and context** — PTIT students and employers need one trusted recruitment flow. Screenshot: homepage.
2. **Product goals** — public discovery, candidate profile, employer publishing, admin moderation. Screenshot: role navigation.
3. **Roles and security** — Candidate, Employer and Admin with JWT and API permissions. Screenshot: login/dashboard.
4. **Architecture** — React client, typed API layer, Django REST Framework, PostgreSQL and role-scoped modules.
5. **Data model** — User, CandidateProfile, Company, Category, Skill, Job and Application relationships. Screenshot: ERD.
6. **Candidate workflow** — skills, experience, CV and application tracking. Screenshot: candidate dashboard.
7. **Employer workflow** — company, job draft, category selection, submit and application transitions. Screenshot: employer workspace.
8. **Admin workflow** — real counts, users, reference data and job moderation. Screenshot: admin dashboard.
9. **Demo data** — idempotent seed command with safe local credentials.
10. **Testing and readiness** — Django checks, focused API tests, TypeScript and production build.
11. **Known limits** — full-suite PostgreSQL/media cleanup depends on local permissions.
12. **Next steps** — richer admin tables and browser E2E automation.
