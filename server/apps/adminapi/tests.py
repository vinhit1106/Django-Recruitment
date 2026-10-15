from datetime import date, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.applications.models import Application
from apps.candidates.models import CandidateCV, CandidateProfile
from apps.companies.models import Company
from apps.jobs.models import Category, Job


PDF = b"%PDF-1.4\n%%EOF"


class AdminApiTests(TestCase):
    def setUp(self):
        password = "A-strong-test-password-123"
        self.admin = User.objects.create_user("phase8-admin@test.example", password, role=User.Role.ADMIN, is_staff=True)
        self.other_admin = User.objects.create_user("phase8-admin2@test.example", password, role=User.Role.ADMIN, is_staff=True)
        self.employer = User.objects.create_user("phase8-employer@test.example", password, role=User.Role.EMPLOYER)
        self.other_employer = User.objects.create_user("phase8-other-employer@test.example", password, role=User.Role.EMPLOYER)
        self.candidate = User.objects.create_user("phase8-candidate@test.example", password, role=User.Role.CANDIDATE)
        self.other_candidate = User.objects.create_user("phase8-other-candidate@test.example", password, role=User.Role.CANDIDATE)
        self.company = Company.objects.create(owner=self.employer, name="Phase 8 Company")
        self.other_company = Company.objects.create(owner=self.other_employer, name="Phase 8 Other Company")
        self.category = Category.objects.create(name="Phase 8 Category", slug="phase-8-category")
        self.client = APIClient()

    def make_job(self, company=None, employer=None, **kwargs):
        company = company or self.company
        employer = employer or company.owner
        values = dict(company=company, category=self.category, created_by=employer, title="Phase 8 Job", description="Job", location="Hanoi", employment_type=Job.EmploymentType.FULL_TIME, deadline=date.today() + timedelta(days=5), status=Job.Status.PENDING)
        values.update(kwargs)
        return Job.objects.create(**values)

    def test_only_admin_can_moderate_and_approve_publishes_job(self):
        job = self.make_job()
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.get("/api/v1/admin/jobs/pending/").data["count"], 1)
        response = self.client.post(f"/api/v1/admin/jobs/{job.id}/approve/")
        self.assertEqual(response.status_code, 200)
        job.refresh_from_db()
        self.assertEqual(job.status, Job.Status.PUBLISHED)
        self.assertEqual(job.reviewed_by_id, self.admin.id)
        self.assertIsNotNone(job.published_at)
        self.client.force_authenticate(self.employer)
        self.assertEqual(self.client.post(f"/api/v1/admin/jobs/{job.id}/approve/").status_code, 403)
        self.client.force_authenticate(self.candidate)
        self.assertEqual(self.client.get("/api/v1/admin/jobs/pending/").status_code, 403)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/v1/admin/jobs/pending/").status_code, 401)

    def test_reject_requires_reason_and_only_pending_transition(self):
        job = self.make_job()
        self.client.force_authenticate(self.admin)
        missing = self.client.post(f"/api/v1/admin/jobs/{job.id}/reject/", {}, format="json")
        self.assertEqual(missing.status_code, 400)
        rejected = self.client.post(f"/api/v1/admin/jobs/{job.id}/reject/", {"reason": "Needs more details"}, format="json")
        self.assertEqual(rejected.status_code, 200)
        job.refresh_from_db()
        self.assertEqual(job.status, Job.Status.REJECTED)
        self.assertEqual(job.rejection_reason, "Needs more details")
        self.assertEqual(self.client.post(f"/api/v1/admin/jobs/{job.id}/approve/").status_code, 400)

    def test_user_management_is_allowlisted_and_protects_last_admin(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get("/api/v1/admin/users/?role=CANDIDATE")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("password", response.data["results"][0])
        updated = self.client.patch(f"/api/v1/admin/users/{self.candidate.id}/", {"is_active": False, "role": "ADMIN", "password": "leak"}, format="json")
        self.assertEqual(updated.status_code, 200)
        self.candidate.refresh_from_db()
        self.assertFalse(self.candidate.is_active)
        self.assertEqual(self.candidate.role, User.Role.CANDIDATE)
        last_admin = self.client.patch(f"/api/v1/admin/users/{self.admin.id}/", {"is_active": False}, format="json")
        self.assertEqual(last_admin.status_code, 200)
        self.client.force_authenticate(self.other_admin)
        # The second admin is now the only active admin and cannot be disabled.
        protected = self.client.patch(f"/api/v1/admin/users/{self.other_admin.id}/", {"is_active": False}, format="json")
        self.assertEqual(protected.status_code, 409)

    def test_category_crud_and_referenced_delete_protection(self):
        self.client.force_authenticate(self.admin)
        created = self.client.post("/api/v1/admin/categories/", {"name": "New Category", "slug": "new-category", "description": "x"}, format="json")
        self.assertEqual(created.status_code, 201)
        duplicate = self.client.post("/api/v1/admin/categories/", {"name": "New Category", "slug": "new-category"}, format="json")
        self.assertEqual(duplicate.status_code, 400)
        job = self.make_job()
        protected = self.client.delete(f"/api/v1/admin/categories/{self.category.id}/")
        self.assertEqual(protected.status_code, 400)
        self.client.force_authenticate(self.employer)
        self.assertEqual(self.client.post("/api/v1/admin/categories/", {"name": "No", "slug": "no"}, format="json").status_code, 403)

    def test_dashboards_are_scoped_and_use_database_counts(self):
        candidate_profile = CandidateProfile.objects.create(user=self.candidate)
        other_profile = CandidateProfile.objects.create(user=self.other_candidate)
        cv = CandidateCV.objects.create(candidate=candidate_profile, file=SimpleUploadedFile("dash.pdf", PDF), original_filename="dash.pdf", file_size=len(PDF))
        other_cv = CandidateCV.objects.create(candidate=other_profile, file=SimpleUploadedFile("other-dash.pdf", PDF), original_filename="other-dash.pdf", file_size=len(PDF))
        own_job = self.make_job(status=Job.Status.PUBLISHED)
        other_job = self.make_job(company=self.other_company, employer=self.other_employer, status=Job.Status.PUBLISHED)
        Application.objects.create(job=own_job, candidate=candidate_profile, cv=cv)
        Application.objects.create(job=other_job, candidate=other_profile, cv=other_cv)

        self.client.force_authenticate(self.candidate)
        candidate_dashboard = self.client.get("/api/v1/dashboard/candidate/")
        self.assertEqual(candidate_dashboard.status_code, 200)
        self.assertEqual(candidate_dashboard.data["application_count"], 1)
        self.client.force_authenticate(self.employer)
        employer_dashboard = self.client.get("/api/v1/employer/dashboard/")
        self.assertEqual(employer_dashboard.status_code, 200)
        self.assertEqual(employer_dashboard.data["company_id"], self.company.id)
        self.assertEqual(employer_dashboard.data["application_count"], 1)
        self.client.force_authenticate(self.admin)
        admin_dashboard = self.client.get("/api/v1/admin/dashboard/")
        self.assertEqual(admin_dashboard.status_code, 200)
        self.assertEqual(admin_dashboard.data["application_count"], 2)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/v1/dashboard/candidate/").status_code, 403)
