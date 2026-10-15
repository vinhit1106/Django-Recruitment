# PostgreSQL schema

The schema below is generated from the implemented Django models and verified against the local PostgreSQL database during the Phase 9 audit.

## Core tables and relationships

- `accounts_user`: email-authenticated users with `CANDIDATE`, `EMPLOYER`, or `ADMIN` role.
- `candidates_candidateprofile`: one-to-one candidate profile.
- `candidates_skill` and `candidates_candidateskill`: shared skills and candidate associations.
- `candidates_experience`: candidate work history.
- `candidates_candidatecv`: private CV metadata and file reference.
- `companies_company`: one company per employer.
- `jobs_category` and `jobs_job`: taxonomy and job postings with moderation fields.
- `applications_application`: candidate application, protected job/candidate/CV references, unique per job and candidate.
- `applications_applicationstatushistory`: append-only status transition audit records.
- `token_blacklist_outstandingtoken` and `token_blacklist_blacklistedtoken`: refresh-token rotation/revocation.

## Integrity rules

- Unique email, employer company owner, candidate profile owner, category name/slug, candidate-skill pair, and job-candidate application pair.
- Salary values are non-negative and `salary_min <= salary_max`.
- Experience end dates cannot precede start dates; current experience has no end date.
- Job, CV, category, and application references use protected deletion where history must remain intact.
- Indexes cover public job visibility, category/company status, candidate experiences, CV status, application status, and status history.

## Verification evidence

The audit introspected PostgreSQL tables and constraints through Django's PostgreSQL connection. The verified database contained all application tables plus Django admin/auth/session and Simple JWT blacklist tables. `migrate --plan` reported no pending operations and `makemigrations --check --dry-run` reported no model drift.
