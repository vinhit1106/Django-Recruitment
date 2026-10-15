from django.db import IntegrityError, transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import ApiErrorResponseSerializer, AuthResponseSerializer, LoginSerializer, LogoutSerializer, RefreshSerializer, RegisterRequestSerializer, RegisterSerializer, UserSerializer

@extend_schema_view(post=extend_schema(
    tags=["Authentication"],
    summary="Register a candidate or employer",
    description="Public endpoint. Required: email and password. Optional: first_name, last_name, role (CANDIDATE by default). Candidate registration also creates its profile. Returns user and JWT pair. No email verification step is implemented.",
    request=RegisterRequestSerializer,
    responses={201: AuthResponseSerializer, 400: ApiErrorResponseSerializer},
    auth=[],
    examples=[OpenApiExample(
        "Candidate registration", request_only=True,
        value={"email": "candidate@example.com", "password": "A-strong-password-123", "first_name": "An", "last_name": "Nguyen", "role": "CANDIDATE"},
    ), OpenApiExample(
        "Employer registration", request_only=True,
        value={"email": "employer@example.com", "password": "A-strong-password-123", "role": "EMPLOYER"},
    )],
))
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        user = self.get_serializer(data=request.data)
        user.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                instance = user.save()
                refresh = RefreshToken.for_user(instance)
        except IntegrityError as exc:
            # Only translate a concurrent email uniqueness violation; other DB errors
            # must propagate rather than being mislabeled as user input errors.
            cause = exc.__cause__
            if getattr(getattr(cause, "diag", None), "constraint_name", None) != "accounts_user_email_key":
                raise
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"email": ["An account with this email already exists."]}) from exc
        return Response({"user": UserSerializer(instance).data, "access": str(refresh.access_token), "refresh": str(refresh)}, status=status.HTTP_201_CREATED)


@extend_schema_view(post=extend_schema(
    tags=["Authentication"], request=LoginSerializer,
    responses={200: AuthResponseSerializer, 400: ApiErrorResponseSerializer, 401: ApiErrorResponseSerializer},
))
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class RefreshView(TokenRefreshView):
    serializer_class = RefreshSerializer


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=LogoutSerializer, responses={204: None})
    def post(self, request):
        token = request.data.get("refresh")
        if not token:
            return Response({"error": {"code": "VALIDATION_ERROR", "message": "Dữ liệu không hợp lệ.", "details": {"refresh": ["Refresh token là bắt buộc."]}}}, status=status.HTTP_400_BAD_REQUEST)
        try:
            RefreshToken(token).blacklist()
        except TokenError:
            return Response({"error": {"code": "INVALID_TOKEN", "message": "Refresh token không hợp lệ hoặc đã bị thu hồi.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
