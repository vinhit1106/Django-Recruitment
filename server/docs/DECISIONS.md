# Architecture decisions

## ADR-001: API base path

Use `/api/v1/` as the versioned API base path, matching the supplied frontend contract.

## ADR-002: Authentication

Use Django's custom email-based user model and Simple JWT. Access tokens are sent in the Authorization header and refresh tokens are sent in JSON request bodies. Refresh rotation and the Simple JWT database blacklist provide revocation on refresh and logout. This decision is implemented in Phase 4 and must be kept in sync with the Frontend token client.

## ADR-003: Database

Use PostgreSQL for the application database. SQLite may be used only for local bootstrapping where PostgreSQL is unavailable, and any constraint or transaction differences must be reported.

## ADR-004: CV files

Treat CVs as private PDF uploads with a 5 MB limit, generated storage names, permission-checked downloads, and no public filesystem exposure. Antivirus scanning is a deployment decision that must be recorded when selected.

## ADR-005: Delivery scope

Implement the smallest monolithic Django/DRF backend that satisfies the supplied endpoint contract. Do not introduce microservices or unrelated dependency upgrades.

## ADR-006: Candidate CV privacy

CV uploads are private records under `MEDIA_ROOT`, with UUID-based storage names, PDF signature validation and a 5 MB limit. Download is served only after owner authorization; public media URLs are not returned. Antivirus scanning is not implemented in this MVP and remains a deployment risk to address before production.

## ADR-007: Candidate profile provisioning

Candidate registration creates one `CandidateProfile` in the same application flow. Candidate endpoints never infer ownership from request payloads and do not silently create a missing profile.

## ADR-008: Public job visibility and employer workflow

Employer job creation always starts in `DRAFT`. The employer can submit a draft or rejected job into `PENDING`; moderation approval remains an Admin phase. Public job endpoints return only `PUBLISHED` jobs whose deadline is today or later. Employer querysets are scoped by the Company owned by the authenticated user.

## ADR-009: Application lifecycle and CV authorization

An Application is created only by its Candidate for a published, unexpired Job with an active CV owned by that Candidate. The database unique constraint prevents duplicate applications. Status changes use an explicit transition endpoint and write an immutable history row within the same transaction. Employers can download a CV only through an Application owned by a Job in their Company; no broad Employer CV endpoint exists.

## ADR-010: Admin safety and dashboard scope

Admin APIs authorize by the business `User.role=ADMIN`, independently of `is_staff`. User management allowlists profile/status fields, never accepts role promotion, and prevents disabling the last active Admin. Dashboard queries are scoped by Candidate/Company ownership or aggregate all database rows only for Admin.

These decisions describe the current implementation and were rechecked during the Phase 9 local integration audit. LAN deployment, antivirus scanning and production storage remain deployment-level decisions.
