from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "created_at")
        read_only_fields = ("id", "role", "created_at")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    role = serializers.ChoiceField(
        choices=[User.Role.CANDIDATE, User.Role.EMPLOYER],
        default=User.Role.CANDIDATE,
        help_text="Public registration accepts CANDIDATE or EMPLOYER only; defaults to CANDIDATE.",
    )

    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name", "role")
        extra_kwargs = {"role": {"required": False}}

    def validate_email(self, value):
        return value.strip().lower()

    def validate(self, attrs):
        # ModelSerializer's uniqueness check runs before email normalization.
        if User.objects.filter(email__iexact=attrs["email"]).exists():
            raise serializers.ValidationError({"email": ["An account with this email already exists."]})
        user = User(**{key: value for key, value in attrs.items() if key != "password"})
        try:
            validate_password(attrs["password"], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        if user.role == User.Role.CANDIDATE:
            from apps.candidates.models import CandidateProfile
            CandidateProfile.objects.create(user=user, full_name=f"{user.first_name} {user.last_name}".strip())
        return user


class RegisterRequestSerializer(serializers.Serializer):
    """Explicit public registration contract used by OpenAPI."""

    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    role = serializers.ChoiceField(
        choices=[User.Role.CANDIDATE, User.Role.EMPLOYER],
        default=User.Role.CANDIDATE,
    )


class AuthResponseSerializer(serializers.Serializer):
    user = UserSerializer(read_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)


class ApiErrorDetailSerializer(serializers.Serializer):
    code = serializers.CharField()
    message = serializers.CharField()
    details = serializers.DictField()


class ApiErrorResponseSerializer(serializers.Serializer):
    error = ApiErrorDetailSerializer()


class LoginSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class RefreshSerializer(TokenRefreshSerializer):
    pass


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
