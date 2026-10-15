# Demo Runbook (5-10 minutes)

1. Start Django and Vite using the commands in `FINAL_COMPLETION_REPORT.md`; open `http://localhost:5173`.
2. On the public page, open Jobs and filter by a category loaded from the API.
3. Sign in as `demo.candidate@example.com`; show profile, seeded skills, experience, CV and application status.
4. Sign in as `demo.employer@example.com`; show Company, the published job and the pending job awaiting moderation.
5. Sign in as `demo.admin@example.com`; show database-backed metrics, users, categories, skills and pending moderation.
6. Approve the pending job. Return to public Jobs and show it after the moderation state changes.

Use the password supplied to `seed_demo_data` for all three demo accounts. Do not commit or present that development password as a production credential.
