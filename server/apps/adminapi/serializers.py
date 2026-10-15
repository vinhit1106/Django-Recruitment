from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from apps.accounts.models import User
from apps.candidates.models import Skill
from apps.jobs.models import Category, Job


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "role", "is_active", "is_staff", "created_at", "updated_at")
        read_only_fields = ("id", "email", "role", "is_staff", "created_at", "updated_at")


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "is_active")


class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tên category là bắt buộc.")
        return value

    def validate_slug(self, value):
        value = value.strip().lower()
        if not value:
            raise serializers.ValidationError("Slug category là bắt buộc.")
        return value


class AdminSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ("id", "name", "is_active")
        read_only_fields = ("id",)

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tên skill là bắt buộc.")
        return value

class ModerationJobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    company = serializers.SerializerMethodField()
    employer = serializers.SerializerMethodField()
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Job
        fields = ("id", "title", "description", "requirements", "benefits", "location", "employment_type", "salary_min", "salary_max", "salary_currency", "deadline", "status", "rejection_reason", "published_at", "reviewed_by", "reviewed_at", "company_name", "company", "employer", "category_name", "created_at", "updated_at")
        read_only_fields = fields

    @extend_schema_field(serializers.DictField())
    def get_company(self, obj):
        return {"id": obj.company_id, "name": obj.company.name, "website": obj.company.website, "address": obj.company.address, "description": obj.company.description}

    @extend_schema_field(serializers.DictField())
    def get_employer(self, obj):
        owner = obj.company.owner
        return {"id": owner.id, "email": owner.email, "full_name": f"{owner.first_name} {owner.last_name}".strip() or owner.email}


class RejectJobSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True, allow_blank=False, max_length=2000)


class DashboardSerializer(serializers.Serializer):
    data = serializers.DictField()
