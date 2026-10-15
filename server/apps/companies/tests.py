from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from .models import Company


class CompanyApiTests(TestCase):
    def setUp(self):
        self.password = "A-strong-test-password-123"
        self.owner = User.objects.create_user("company-owner@test.example", self.password, role=User.Role.EMPLOYER)
        self.other = User.objects.create_user("company-other@test.example", self.password, role=User.Role.EMPLOYER)
        self.candidate = User.objects.create_user("company-candidate@test.example", self.password, role=User.Role.CANDIDATE)
        self.client = APIClient()

    def test_owner_can_create_read_and_patch_company(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post("/api/v1/employer/company/", {"name": "Owner Company", "website": "https://example.com"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "Owner Company")
        self.assertEqual(self.client.get("/api/v1/employer/company/").status_code, 200)
        patched = self.client.patch("/api/v1/employer/company/", {"name": "Updated Company", "owner_id": self.other.id}, format="json")
        self.assertEqual(patched.status_code, 200)
        self.assertEqual(patched.data["name"], "Updated Company")
        self.assertFalse(Company.objects.filter(owner=self.other).exists())

    def test_duplicate_and_non_employer_management_are_blocked(self):
        Company.objects.create(owner=self.owner, name="Existing")
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.post("/api/v1/employer/company/", {"name": "Second"}, format="json").status_code, 409)
        self.client.force_authenticate(self.candidate)
        self.assertEqual(self.client.get("/api/v1/employer/company/").status_code, 403)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/v1/employer/company/").status_code, 401)

    def test_public_company_does_not_expose_owner(self):
        company = Company.objects.create(owner=self.owner, name="Public Company", description="Public")
        response = self.client.get(f"/api/v1/companies/{company.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("owner", response.data)
        self.assertNotIn("email", response.data)
