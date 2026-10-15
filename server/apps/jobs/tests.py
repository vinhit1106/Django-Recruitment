from datetime import date, timedelta

from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.companies.models import Company

from .models import Category, Job


class JobsApiTests(TestCase):
    def setUp(self):
        self.password = "A-strong-test-password-123"
        self.owner = User.objects.create_user("job-owner@test.example", self.password, role=User.Role.EMPLOYER)
        self.other = User.objects.create_user("job-other@test.example", self.password, role=User.Role.EMPLOYER)
        self.candidate = User.objects.create_user("job-candidate@test.example", self.password, role=User.Role.CANDIDATE)
        self.company = Company.objects.create(owner=self.owner, name="Jobs Company")
        self.other_company = Company.objects.create(owner=self.other, name="Other Company")
        self.category = Category.objects.create(name="Engineering", slug="engineering")
        self.client = APIClient()

    def make_job(self, **kwargs):
        values = dict(company=self.company, category=self.category, created_by=self.owner, title="Backend Engineer", description="Django role", requirements="Python", location="Hanoi", employment_type=Job.EmploymentType.FULL_TIME, deadline=date.today() + timedelta(days=10), status=Job.Status.DRAFT)
        values.update(kwargs)
        return Job.objects.create(**values)

    def test_employer_crud_is_scoped_and_default_is_draft(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post("/api/v1/employer/jobs/", {"title": "New Job", "description": "Description", "location": "Hanoi", "employment_type": "FULL_TIME", "deadline": str(date.today() + timedelta(days=5)), "category_id": self.category.id}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "DRAFT")
        job = Job.objects.get(pk=response.data["id"])
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(f"/api/v1/employer/jobs/{job.id}/").status_code, 404)
        self.client.force_authenticate(self.candidate)
        self.assertEqual(self.client.post("/api/v1/employer/jobs/", {}, format="json").status_code, 403)

    def test_employer_job_preserves_multiline_text_fields(self):
        self.client.force_authenticate(self.owner)
        values = {
            "title": "Multiline Product Engineer",
            "description": "Build features.\nCollaborate with design and product.",
            "requirements": "Python and Django\nREST API experience\n\nClear communication",
            "benefits": "Flexible hours\nHealth insurance\nLearning budget",
            "location": "Hanoi / Remote",
            "employment_type": "FULL_TIME",
            "deadline": str(date.today() + timedelta(days=10)),
            "category_id": self.category.id,
        }
        response = self.client.post("/api/v1/employer/jobs/", values, format="json")
        self.assertEqual(response.status_code, 201)
        job = Job.objects.get(pk=response.data["id"])
        self.assertEqual(job.description, values["description"])
        self.assertEqual(job.requirements, values["requirements"])
        self.assertEqual(job.benefits, values["benefits"])
        self.assertEqual(response.data["requirements"], values["requirements"])
        self.assertEqual(response.data["benefits"], values["benefits"])
        submitted = self.client.post(f"/api/v1/employer/jobs/{job.id}/submit/")
        self.assertEqual(submitted.status_code, 200)
        self.assertEqual(submitted.data["description"], values["description"])
        self.assertEqual(submitted.data["requirements"], values["requirements"])
        self.assertEqual(submitted.data["benefits"], values["benefits"])

    def test_employer_without_company_is_rejected(self):
        no_company = User.objects.create_user("no-company@test.example", self.password, role=User.Role.EMPLOYER)
        self.client.force_authenticate(no_company)
        response = self.client.post("/api/v1/employer/jobs/", {}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"]["code"], "COMPANY_REQUIRED")

    def test_public_visibility_filters_status_and_deadline(self):
        visible = self.make_job(status=Job.Status.PUBLISHED)
        self.make_job(title="Draft", status=Job.Status.DRAFT)
        self.make_job(title="Closed", status=Job.Status.CLOSED)
        self.make_job(title="Expired", status=Job.Status.PUBLISHED, deadline=date.today() - timedelta(days=1))
        response = self.client.get("/api/v1/jobs/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], visible.id)
        self.assertEqual(self.client.get("/api/v1/jobs/999999/").status_code, 404)

    def test_search_filters_ordering_and_validation(self):
        self.make_job(status=Job.Status.PUBLISHED, title="Python Django", salary_min=1000, salary_max=2000, location="Hanoi")
        self.make_job(status=Job.Status.PUBLISHED, title="Frontend", salary_min=500, salary_max=900, location="Da Nang")
        self.assertEqual(self.client.get("/api/v1/jobs/?search=django").data["count"], 2)
        self.assertEqual(self.client.get("/api/v1/jobs/?location=da%20nang").data["count"], 1)
        self.assertEqual(self.client.get("/api/v1/jobs/?salary_min=1500").data["count"], 1)
        invalid = self.client.get("/api/v1/jobs/?salary_min=not-number")
        self.assertEqual(invalid.status_code, 200)
        self.assertEqual(invalid.data["count"], 0)
        self.client.force_authenticate(self.owner)
        invalid_salary = self.client.post("/api/v1/employer/jobs/", {"title": "Bad", "description": "x", "location": "Hanoi", "employment_type": "FULL_TIME", "deadline": str(date.today() + timedelta(days=1)), "category_id": self.category.id, "salary_min": 10, "salary_max": 1}, format="json")
        self.assertEqual(invalid_salary.status_code, 400)

    def test_submit_and_close_transitions(self):
        job = self.make_job()
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.post(f"/api/v1/employer/jobs/{job.id}/submit/").status_code, 200)
        job.refresh_from_db(); self.assertEqual(job.status, Job.Status.PENDING)
        self.assertEqual(self.client.post(f"/api/v1/employer/jobs/{job.id}/close/").status_code, 200)
        job.refresh_from_db(); self.assertEqual(job.status, Job.Status.CLOSED)
