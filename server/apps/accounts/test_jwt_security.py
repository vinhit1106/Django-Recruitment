from datetime import timedelta
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from apps.accounts.models import User

class JwtSecurityVerificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.password = "A-strong-test-password-123"
        self.user = User.objects.create_user("jwt-verify@example.test", self.password)

    def test_invalid_access_token_and_missing_bearer_are_rejected(self):
        self.assertEqual(self.client.get("/api/v1/auth/me/").status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer definitely.invalid")
        self.assertEqual(self.client.get("/api/v1/auth/me/").status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION="Token definitely.invalid")
        self.assertEqual(self.client.get("/api/v1/auth/me/").status_code, 401)

    def test_access_token_expiry_is_enforced(self):
        token = AccessToken.for_user(self.user)
        token.set_exp(lifetime=timedelta(seconds=-1))
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(self.client.get("/api/v1/auth/me/").status_code, 401)

    def test_refresh_rotation_old_token_is_rejected(self):
        login = self.client.post("/api/v1/auth/login/", {"email": self.user.email, "password": self.password}, format="json")
        old_refresh = login.data["refresh"]
        rotated = self.client.post("/api/v1/auth/refresh/", {"refresh": old_refresh}, format="json")
        self.assertEqual(rotated.status_code, 200)
        self.assertEqual(self.client.post("/api/v1/auth/refresh/", {"refresh": old_refresh}, format="json").status_code, 401)

    def test_logout_blacklists_current_refresh_only(self):
        login = self.client.post("/api/v1/auth/login/", {"email": self.user.email, "password": self.password}, format="json")
        access, refresh = login.data["access"], login.data["refresh"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        self.assertEqual(self.client.post("/api/v1/auth/logout/", {"refresh": refresh}, format="json").status_code, 204)
        self.assertEqual(self.client.post("/api/v1/auth/refresh/", {"refresh": refresh}, format="json").status_code, 401)
        self.assertEqual(self.client.get("/api/v1/auth/me/").status_code, 200)

    def test_cors_preflight_allows_authorization_only_for_configured_origin(self):
        with override_settings(CORS_ALLOWED_ORIGINS=["http://192.168.1.110:5173"]):
            allowed = self.client.options("/api/v1/auth/login/", HTTP_ORIGIN="http://192.168.1.110:5173", HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST", HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type,authorization")
            self.assertEqual(allowed.status_code, 200)
            self.assertEqual(allowed["Access-Control-Allow-Origin"], "http://192.168.1.110:5173")
            self.assertIn("authorization", allowed["Access-Control-Allow-Headers"].lower())
            denied = self.client.options("/api/v1/auth/login/", HTTP_ORIGIN="http://evil.example", HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST", HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type,authorization")
            self.assertNotIn("Access-Control-Allow-Origin", denied)
