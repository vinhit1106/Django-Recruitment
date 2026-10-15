import os
from pathlib import Path
from django.conf import settings
from django.db import IntegrityError
from rest_framework import serializers
from .models import CandidateCV, CandidateProfile, CandidateSkill, Experience, Skill

class CandidateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateProfile
        fields = ("id", "full_name", "phone", "location", "summary", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")
    def validate_phone(self, value):
        value = value.strip()
        if value and (len(value) < 7 or len(value) > 30):
            raise serializers.ValidationError("Số điện thoại không hợp lệ.")
        return value

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ("id", "name", "is_active")
        read_only_fields = fields

class CandidateSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(source="skill", queryset=Skill.objects.filter(is_active=True), write_only=True)
    class Meta:
        model = CandidateSkill
        fields = ("id", "skill", "skill_id", "created_at")
        read_only_fields = ("id", "skill", "created_at")
    def validate(self, attrs):
        candidate = self.context["request"].user.candidate_profile
        if CandidateSkill.objects.filter(candidate=candidate, skill=attrs["skill"]).exists():
            raise serializers.ValidationError({"skill_id": ["Kỹ năng này đã có trong hồ sơ."]})
        return attrs
    def create(self, validated_data):
        try:
            return CandidateSkill.objects.create(candidate=self.context["request"].user.candidate_profile, **validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError({"skill_id": ["Kỹ năng này đã có trong hồ sơ."]}) from exc

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ("id", "company_name", "job_title", "description", "start_date", "end_date", "is_current", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")
    def validate(self, attrs):
        start = attrs.get("start_date", getattr(self.instance, "start_date", None))
        end = attrs.get("end_date", getattr(self.instance, "end_date", None))
        current = attrs.get("is_current", getattr(self.instance, "is_current", False))
        if start and end and start > end:
            raise serializers.ValidationError({"end_date": ["Ngày kết thúc phải sau hoặc bằng ngày bắt đầu."]})
        if current and end is not None:
            raise serializers.ValidationError({"end_date": ["Kinh nghiệm hiện tại không được có ngày kết thúc."]})
        if current:
            attrs["end_date"] = None
        return attrs
    def create(self, validated_data):
        return Experience.objects.create(candidate=self.context["request"].user.candidate_profile, **validated_data)

class CandidateCVSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True, required=False)
    class Meta:
        model = CandidateCV
        fields = ("id", "file", "original_filename", "file_size", "content_type", "status", "created_at", "updated_at")
        read_only_fields = ("id", "original_filename", "file_size", "content_type", "created_at", "updated_at")
    def validate_file(self, value):
        if value.size > int(getattr(settings, "MAX_CV_UPLOAD_SIZE", 5 * 1024 * 1024)):
            raise serializers.ValidationError("CV không được vượt quá 5 MB.")
        if Path(value.name).suffix.lower() != ".pdf":
            raise serializers.ValidationError("CV phải có định dạng PDF.")
        header = value.read(5); value.seek(0)
        if header != b"%PDF-":
            raise serializers.ValidationError("Nội dung file không phải PDF hợp lệ.")
        return value
    def create(self, validated_data):
        if "file" not in validated_data:
            raise serializers.ValidationError({"file": ["File CV là bắt buộc."]})
        upload = validated_data.pop("file")
        return CandidateCV.objects.create(candidate=self.context["request"].user.candidate_profile, file=upload, original_filename=os.path.basename(upload.name)[:255], file_size=upload.size, content_type="application/pdf", **validated_data)
