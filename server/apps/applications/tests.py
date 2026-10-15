from datetime import date, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.candidates.models import CandidateCV, CandidateProfile
from apps.companies.models import Company
from apps.jobs.models import Category, Job

from .models import Application, ApplicationStatusHistory


PDF = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF"


class ApplicationApiTests(TestCase):
    def setUp(self):
        password = "A-strong-test-password-123"
        self.candidate = User.objects.create_user("application-candidate@test.example", password, role=User.Role.CANDIDATE)
        self.other_candidate = User.objects.create_user("application-other@test.example", password, role=User.Role.CANDIDATE)
        self.employer = User.objects.create_user("application-employer@test.example", password, role=User.Role.EMPLOYER)
        self.other_employer = User.objects.create_user("application-other-employer@test.example", password, role=User.Role.EMPLOYER)
        self.profile = CandidateProfile.objects.create(user=self.candidate)
        self.other_profile = CandidateProfile.objects.create(user=self.other_candidate)
        self.company = Company.objects.create(owner=self.employer, name="Application Company")
        self.other_company = Company.objects.create(owner=self.other_employer, name="Other Application Company")
        self.category = Category.objects.create(name="Application Category", slug="application-category")
        self.job = self.make_job()
        self.cv = CandidateCV.objects.create(candidate=self.profile, file=SimpleUploadedFile("candidate.pdf", PDF), original_filename="candidate.pdf", file_size=len(PDF))
        self.other_cv = CandidateCV.objects.create(candidate=self.other_profile, file=SimpleUploadedFile("other.pdf", PDF), original_filename="other.pdf", file_size=len(PDF))
        self.client = APIClient()

    def tearDown(self):
        ApplicationStatusHistory.objects.all().delete()
        Application.objects.all().delete()
        CandidateCV.objects.all().delete()

    def make_job(self, **kwargs):
        values = dict(company=self.company, category=self.category, created_by=self.employer, title="Application Job", description="Role", location="Hanoi", employment_type=Job.EmploymentType.FULL_TIME, deadline=date.today() + timedelta(days=5), status=Job.Status.PUBLISHED)
        values.update(kwargs)
        return Job.objects.create(**values)

    def apply(self, user=None, **payload):
        self.client.force_authenticate(user or self.candidate)
        data = {"job_id": self.job.id, "cv_id": self.cv.id, "cover_letter": "Interested"}
        data.update(payload)
        return self.client.post("/api/v1/candidate/applications/", data, format="json")

    def test_candidate_can_apply_and_get_own_application(self):
        response = self.apply()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], Application.Status.SUBMITTED)
        application = Application.objects.get(pk=response.data["id"])
        self.assertEqual(ApplicationStatusHistory.objects.filter(application=application).count(), 1)
        self.assertEqual(self.client.get("/api/v1/candidate/applications/").data["count"], 1)
        self.assertEqual(self.client.get(f"/api/v1/candidate/applications/{application.id}/").status_code, 200)
        self.client.force_authenticate(self.other_candidate)
        self.assertEqual(self.client.get(f"/api/v1/candidate/applications/{application.id}/").status_code, 404)

    def test_apply_rejects_ineligible_job_other_cv_and_duplicate(self):
        self.assertEqual(self.apply(cv_id=self.other_cv.id).status_code, 400)
        self.job.status = Job.Status.DRAFT; self.job.save()
        self.assertEqual(self.apply().status_code, 400)
        self.job.status = Job.Status.PUBLISHED; self.job.deadline = date.today() - timedelta(days=1); self.job.save()
        self.assertEqual(self.apply().status_code, 400)
        self.job.deadline = date.today() + timedelta(days=5); self.job.save()
        self.assertEqual(self.apply().status_code, 201)
        duplicate = self.apply()
        self.assertIn(duplicate.status_code, {400, 409})

    def test_database_unique_constraint_blocks_duplicate_application(self):
        Application.objects.create(job=self.job, candidate=self.profile, cv=self.cv)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Application.objects.create(job=self.job, candidate=self.profile, cv=self.cv)

    def test_candidate_withdrawal_only_for_allowed_states(self):
        application = Application.objects.create(job=self.job, candidate=self.profile, cv=self.cv)
        self.client.force_authenticate(self.candidate)
        response = self.client.post(f"/api/v1/candidate/applications/{application.id}/withdraw/")
        self.assertEqual(response.status_code, 200)
        application.refresh_from_db(); self.assertEqual(application.status, Application.Status.WITHDRAWN)
        self.assertEqual(ApplicationStatusHistory.objects.filter(application=application).count(), 1)
        response = self.client.post(f"/api/v1/candidate/applications/{application.id}/withdraw/")
        self.assertEqual(response.status_code, 400)

    def test_employer_scope_transition_history_and_cv_download(self):
        application = Application.objects.create(job=self.job, candidate=self.profile, cv=self.cv)
        self.client.force_authenticate(self.employer)
        self.assertEqual(self.client.get("/api/v1/employer/applications/").data["count"], 1)
        response = self.client.post(f"/api/v1/employer/applications/{application.id}/transition/", {"status": "REVIEWING", "note": "Viewed"}, format="json")
        self.assertEqual(response.status_code, 200)
        application.refresh_from_db(); self.assertEqual(application.status, Application.Status.REVIEWING)
        history = ApplicationStatusHistory.objects.get(application=application)
        self.assertEqual((history.previous_status, history.new_status), (Application.Status.SUBMITTED, Application.Status.REVIEWING))
        download = self.client.get(f"/api/v1/employer/applications/{application.id}/cv/download/")
        self.assertEqual(download.status_code, 200)
        self.assertEqual(download["Content-Type"], "application/pdf")
        self.client.force_authenticate(self.other_employer)
        self.assertEqual(self.client.get(f"/api/v1/employer/applications/{application.id}/").status_code, 404)
        self.assertEqual(self.client.get(f"/api/v1/employer/applications/{application.id}/cv/download/").status_code, 404)

    def test_transition_rejects_invalid_and_non_employer(self):
        application = Application.objects.create(job=self.job, candidate=self.profile, cv=self.cv)
        self.client.force_authenticate(self.employer)
        invalid = self.client.post(f"/api/v1/employer/applications/{application.id}/transition/", {"status": "HIRED"}, format="json")
        self.assertEqual(invalid.status_code, 400)
        application.refresh_from_db(); self.assertEqual(application.status, Application.Status.SUBMITTED)
        self.client.force_authenticate(self.candidate)
        self.assertEqual(self.client.post(f"/api/v1/employer/applications/{application.id}/transition/", {"status": "REVIEWING"}, format="json").status_code, 403)

    def test_guest_cannot_manage_applications(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/v1/candidate/applications/").status_code, 401)
        self.assertEqual(self.client.get("/api/v1/employer/applications/").status_code, 401)
