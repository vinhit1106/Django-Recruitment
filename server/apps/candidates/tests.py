from datetime import date
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.applications.models import Application
from apps.companies.models import Company
from apps.jobs.models import Category, Job

from .models import CandidateCV, CandidateProfile, Experience, Skill


PDF = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF"


class CandidateApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.password = "A-strong-test-password-123"
        self.candidate = User.objects.create_user("candidate-five@example.test", self.password, role=User.Role.CANDIDATE)
        self.other = User.objects.create_user("other-five@example.test", self.password, role=User.Role.CANDIDATE)
        self.employer = User.objects.create_user("employer-five@example.test", self.password, role=User.Role.EMPLOYER)
        CandidateProfile.objects.create(user=self.candidate)
        CandidateProfile.objects.create(user=self.other)
        self.client.force_authenticate(self.candidate)

    def tearDown(self):
        Application.objects.all().delete()
        Job.objects.all().delete()
        Company.objects.all().delete()
        Category.objects.all().delete()
        CandidateCV.objects.all().delete()
        User.objects.filter(email__contains="-five@example.test").delete()

    def test_profile_is_owned_and_system_fields_are_read_only(self):
        response = self.client.get("/api/v1/candidate/profile/")
        self.assertEqual(response.status_code, 200)
        response = self.client.patch("/api/v1/candidate/profile/", {"full_name": "Candidate Five", "user_id": self.other.id, "email": "hijack@example.test"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.candidate.refresh_from_db()
        self.assertEqual(self.candidate.email, "candidate-five@example.test")
        self.assertEqual(self.candidate.candidate_profile.full_name, "Candidate Five")

    def test_non_candidate_and_guest_are_denied(self):
        self.client.force_authenticate(self.employer)
        self.assertEqual(self.client.get("/api/v1/candidate/profile/").status_code, 403)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/v1/candidate/profile/").status_code, 401)

    def test_skills_are_scoped_and_duplicate_is_rejected(self):
        skill = Skill.objects.create(name="Django")
        first = self.client.post("/api/v1/candidate/skills/", {"skill_id": skill.id}, format="json")
        self.assertEqual(first.status_code, 201)
        duplicate = self.client.post("/api/v1/candidate/skills/", {"skill_id": skill.id}, format="json")
        self.assertEqual(duplicate.status_code, 400)
        self.assertEqual(self.client.get("/api/v1/candidate/skills/").data["count"], 1)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.delete(f"/api/v1/candidate/skills/{first.data['id']}/").status_code, 404)

    def test_public_skill_catalog_only_returns_active_skills(self):
        Skill.objects.create(name="Django", is_active=True)
        Skill.objects.create(name="Legacy", is_active=False)
        self.client.force_authenticate(None)
        response = self.client.get("/api/v1/candidate/skills/catalog/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["name"] for item in response.data["results"]], ["Django"])

    def test_experience_validation_and_crud(self):
        invalid = self.client.post("/api/v1/candidate/experiences/", {"company_name": "X", "job_title": "Dev", "start_date": "2025-01-01", "end_date": "2024-01-01"}, format="json")
        self.assertEqual(invalid.status_code, 400)
        created = self.client.post("/api/v1/candidate/experiences/", {"company_name": "X", "job_title": "Dev", "start_date": "2024-01-01", "is_current": True}, format="json")
        self.assertEqual(created.status_code, 201)
        self.assertIsNone(created.data["end_date"])
        updated = self.client.patch(f"/api/v1/candidate/experiences/{created.data['id']}/", {"job_title": "Senior Dev"}, format="json")
        self.assertEqual(updated.status_code, 200)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(f"/api/v1/candidate/experiences/{created.data['id']}/").status_code, 404)

    def test_private_cv_upload_download_and_validation(self):
        valid = SimpleUploadedFile("../../resume.pdf", PDF, content_type="text/plain")
        uploaded = self.client.post("/api/v1/candidate/cvs/", {"file": valid}, format="multipart")
        self.assertEqual(uploaded.status_code, 201)
        self.assertEqual(uploaded.data["original_filename"], "resume.pdf")
        self.assertNotIn("media/", uploaded.data.get("file", ""))
        downloaded = self.client.get(f"/api/v1/candidate/cvs/{uploaded.data['id']}/download/")
        self.assertEqual(downloaded.status_code, 200)
        self.assertEqual(downloaded["Content-Type"], "application/pdf")
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(f"/api/v1/candidate/cvs/{uploaded.data['id']}/download/").status_code, 404)

        self.client.force_authenticate(self.candidate)
        bad = SimpleUploadedFile("resume.txt", b"not pdf", content_type="application/pdf")
        self.assertEqual(self.client.post("/api/v1/candidate/cvs/", {"file": bad}, format="multipart").status_code, 400)
        too_large = SimpleUploadedFile("large.pdf", b"%PDF-" + b"x" * (5 * 1024 * 1024), content_type="application/pdf")
        self.assertEqual(self.client.post("/api/v1/candidate/cvs/", {"file": too_large}, format="multipart").status_code, 400)

    def test_cv_referenced_by_application_cannot_be_deleted(self):
        cv = CandidateCV.objects.create(candidate=self.candidate.candidate_profile, file=SimpleUploadedFile("ref.pdf", PDF), original_filename="ref.pdf", file_size=len(PDF))
        company = Company.objects.create(owner=self.employer, name="Five Company")
        category = Category.objects.create(name="Five Category", slug="five-category")
        job = Job.objects.create(company=company, category=category, created_by=self.employer, title="Five Job", description="x", location="Hanoi", employment_type=Job.EmploymentType.FULL_TIME, deadline=date(2030, 1, 1), status=Job.Status.PUBLISHED)
        Application.objects.create(job=job, candidate=self.candidate.candidate_profile, cv=cv)
        response = self.client.delete(f"/api/v1/candidate/cvs/{cv.id}/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"]["details"]["code"], "CV_IN_USE")
