# ERD

Phase 3 implements the following entity groups:

```text
User 1--1 CandidateProfile
CandidateProfile 1--* CandidateCV
CandidateProfile 1--* CandidateSkill *--1 Skill
CandidateProfile 1--* Experience
User (employer) 1--* Company
Company 1--* Job *--1 Category
Job 1--* Application *--1 CandidateProfile
CandidateCV 1--* Application
Application 1--* ApplicationStatusHistory
```

Database protections implemented include unique `(job_id, candidate_id)` applications, unique `(candidate_id, skill_id)` pairs, non-negative and ordered salaries, valid experience dates, protected references from applications to CVs/jobs/candidates, and indexes for public jobs, job status, candidates and applications.

## Implemented model notes

- `CandidateProfile` is one-to-one with `User`.
- `Company` is one-to-one with its employer owner for the MVP.
- `CandidateCV.file` is stored below the private media root; upload validation and authorization-checked download are implemented.
- `Application.cv` uses `PROTECT` so an application cannot lose its referenced CV history.
- `Job.company`, `Job.category`, and `Job.created_by` use `PROTECT` to prevent silent historical data loss.
- Candidate API ownership is enforced by filtering every skills, experience and CV queryset through the authenticated user's profile.
- Company ownership is one-to-one with an Employer, and Job management is scoped through that Company. Public job visibility is a queryset rule over status and deadline; no schema change was needed in Phase 6.
- Application creation and each status transition create `ApplicationStatusHistory`. Application-to-CV, Application-to-Candidate and Application-to-Job references are protected to preserve audit history and CV access is authorized through Application ownership.
- Phase 8 uses existing `Job.reviewed_by`, `Job.reviewed_at`, `Job.published_at` and `Job.rejection_reason` fields for moderation audit; no schema change was needed.
