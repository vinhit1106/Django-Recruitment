from unittest.mock import patch

from django.test import TestCase
from drf_spectacular.generators import SchemaGenerator
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from apps.candidates.models import CandidateProfile


class AuthenticationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.password = "A-strong-test-password-123"
        self.email = "auth-test@example.test"

    def tearDown(self):
        User.objects.filter(email__in=[self.email, "employer-test@example.test"]).delete()

    def test_register_returns_tokens_and_hashes_password(self):
        response = self.client.post("/api/v1/auth/register/", {"email": self.email, "password": self.password, "role": "EMPLOYER"}, format="json")
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email=self.email)
        self.assertEqual(user.role, User.Role.EMPLOYER)
        self.assertTrue(user.check_password(self.password))
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_admin_registration_is_rejected(self):
        response = self.client.post("/api/v1/auth/register/", {"email": self.email, "password": self.password, "role": "ADMIN"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
        self.assertFalse(User.objects.filter(email=self.email).exists())

    def test_login_me_refresh_and_logout_blacklist(self):
        User.objects.create_user(self.email, self.password)
        login = self.client.post("/api/v1/auth/login/", {"email": self.email, "password": self.password}, format="json")
        self.assertEqual(login.status_code, 200)
        access = login.data["access"]
        refresh = login.data["refresh"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        me = self.client.get("/api/v1/auth/me/")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.data["email"], self.email)

        refreshed = self.client.post("/api/v1/auth/refresh/", {"refresh": refresh}, format="json")
        self.assertEqual(refreshed.status_code, 200)
        self.assertIn("access", refreshed.data)

        logout = self.client.post("/api/v1/auth/logout/", {"refresh": refreshed.data.get("refresh", refresh)}, format="json")
        self.assertEqual(logout.status_code, 204)
        rejected = self.client.post("/api/v1/auth/refresh/", {"refresh": refreshed.data.get("refresh", refresh)}, format="json")
        self.assertEqual(rejected.status_code, 401)

    def test_guest_cannot_access_me(self):
        response = self.client.get("/api/v1/auth/me/")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["error"]["code"], "AUTHENTICATION_ERROR")

    def test_minimal_registration_defaults_to_candidate_and_creates_profile(self):
        response = self.client.post("/api/v1/auth/register/", {"email": "NEW.Candidate@example.test", "password": self.password}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(set(response.data), {"user", "access", "refresh"})
        self.assertNotIn("password", response.data["user"])
        self.assertEqual(response.data["user"]["role"], User.Role.CANDIDATE)
        user = User.objects.get(email="new.candidate@example.test")
        self.assertTrue(CandidateProfile.objects.filter(user=user).exists())
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        self.assertEqual(self.client.get("/api/v1/candidate/profile/").status_code, 200)

    def test_registration_names_and_employer_role(self):
        response = self.client.post("/api/v1/auth/register/", {"email": self.email, "password": self.password, "first_name": "An", "last_name": "Nguyen", "role": "EMPLOYER"}, format="json")
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(pk=response.data["user"]["id"])
        self.assertEqual(user.first_name, "An")
        self.assertEqual(user.last_name, "Nguyen")
        self.assertFalse(CandidateProfile.objects.filter(user=user).exists())

    def test_registration_missing_invalid_and_weak_inputs(self):
        for payload, field in [
            ({"password": self.password}, "email"),
            ({"email": self.email}, "password"),
            ({"email": "not-an-email", "password": self.password}, "email"),
            ({"email": self.email, "password": "short"}, "password"),
            ({"email": self.email, "password": "password"}, "password"),
            ({"email": self.email, "password": self.password, "role": "UNKNOWN"}, "role"),
        ]:
            with self.subTest(field=field, payload_keys=list(payload)):
                response = self.client.post("/api/v1/auth/register/", payload, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.data["error"]["code"], "VALIDATION_ERROR")
                self.assertIn(field, response.data["error"]["details"])
        self.assertFalse(User.objects.filter(email=self.email).exists())

    def test_password_may_resemble_email_when_other_password_rules_pass(self):
        response = self.client.post("/api/v1/auth/register/", {"email": "linh@example.test", "password": "linh@example.test-42"}, format="json")
        self.assertEqual(response.status_code, 201)

    def test_duplicate_email_including_different_case_is_validation_error(self):
        existing = User.objects.create_user(self.email, self.password)
        for email in [self.email, self.email.upper()]:
            with self.subTest(email=email):
                response = self.client.post("/api/v1/auth/register/", {"email": email, "password": self.password}, format="json")
                self.assertEqual(response.status_code, 400)
                self.assertIn("email", response.data["error"]["details"])
        existing.refresh_from_db()
        self.assertTrue(existing.check_password(self.password))
        self.assertEqual(User.objects.filter(email__iexact=self.email).count(), 1)

    def test_registration_ignores_privilege_fields_and_expired_authorization(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer expired.invalid.token")
        response = self.client.post("/api/v1/auth/register/", {"email": self.email, "password": self.password, "is_staff": True, "is_superuser": True, "is_active": False}, format="json")
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(pk=response.data["user"]["id"])
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_profile_failure_rolls_back_user_creation(self):
        with patch("apps.candidates.models.CandidateProfile.objects.create", side_effect=RuntimeError("Profile unavailable")):
            with self.assertRaises(RuntimeError):
                self.client.post("/api/v1/auth/register/", {"email": self.email, "password": self.password}, format="json")
        self.assertFalse(User.objects.filter(email=self.email).exists())

    def test_registration_cors_preflight_for_configured_frontend(self):
        with self.settings(CORS_ALLOWED_ORIGINS=["http://192.168.1.110:5173"]):
            response = self.client.options("/api/v1/auth/register/", HTTP_ORIGIN="http://192.168.1.110:5173", HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST", HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Access-Control-Allow-Origin"], "http://192.168.1.110:5173")
            self.assertIn("POST", response["Access-Control-Allow-Methods"])
            rejected = self.client.options("/api/v1/auth/register/", HTTP_ORIGIN="http://untrusted.example", HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST")
            self.assertNotIn("Access-Control-Allow-Origin", rejected)

    def test_openapi_registration_contract_matches_request_and_runtime_response(self):
        schema = SchemaGenerator().get_schema(request=None, public=True)
        operation = schema["paths"]["/api/v1/auth/register/"]["post"]
        components = schema["components"]["schemas"]

        def resolve(value):
            if "$ref" in value:
                return components[value["$ref"].split("/")[-1]]
            if "allOf" in value:
                return resolve(value["allOf"][0])
            return value

        request_schema = resolve(operation["requestBody"]["content"]["application/json"]["schema"])
        self.assertEqual(set(request_schema["required"]), {"email", "password"})
        self.assertEqual(set(request_schema["properties"]), {"email", "password", "first_name", "last_name", "role"})
        role = request_schema["properties"]["role"]
        self.assertEqual(set(resolve(role)["enum"]), {"CANDIDATE", "EMPLOYER"})
        self.assertEqual(role["default"], "CANDIDATE")
        self.assertFalse(any(item for item in operation.get("security", [])))
        response_schema = resolve(operation["responses"]["201"]["content"]["application/json"]["schema"])
        response = self.client.post("/api/v1/auth/register/", {"email": self.email, "password": self.password}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(set(response_schema["properties"]), set(response.data))
        error_schema = resolve(operation["responses"]["400"]["content"]["application/json"]["schema"])
        self.assertIn("error", error_schema["properties"])
