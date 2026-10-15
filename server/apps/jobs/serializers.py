from datetime import date

from rest_framework import serializers

from apps.companies.serializers import PublicCompanySerializer

from .models import Category, Job


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description")
        read_only_fields = fields


class PublicJobSerializer(serializers.ModelSerializer):
    company = PublicCompanySerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Job
        fields = ("id", "title", "description", "requirements", "benefits", "location", "employment_type", "salary_min", "salary_max", "salary_currency", "deadline", "status", "published_at", "created_at", "updated_at", "company", "category")
        read_only_fields = fields


class EmployerJobSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(source="category", queryset=Category.objects.filter(is_active=True), write_only=True, required=True)
    category = CategorySerializer(read_only=True)
    company = PublicCompanySerializer(read_only=True)

    class Meta:
        model = Job
        fields = ("id", "title", "description", "requirements", "benefits", "location", "employment_type", "salary_min", "salary_max", "salary_currency", "deadline", "status", "rejection_reason", "published_at", "created_at", "updated_at", "company", "category", "category_id")
        read_only_fields = ("id", "status", "rejection_reason", "published_at", "created_at", "updated_at", "company", "category")

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Tiêu đề là bắt buộc.")
        return value

    def validate_deadline(self, value):
        if value < date.today():
            raise serializers.ValidationError("Hạn nộp phải từ hôm nay trở đi.")
        return value

    def validate(self, attrs):
        minimum = attrs.get("salary_min", getattr(self.instance, "salary_min", None))
        maximum = attrs.get("salary_max", getattr(self.instance, "salary_max", None))
        if minimum is not None and maximum is not None and minimum > maximum:
            raise serializers.ValidationError({"salary_max": ["Mức lương tối đa phải lớn hơn hoặc bằng mức lương tối thiểu."]})
        return attrs

