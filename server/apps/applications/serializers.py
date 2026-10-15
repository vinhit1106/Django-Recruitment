from datetime import date

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from apps.candidates.models import CandidateCV
from apps.jobs.models import Job
from apps.jobs.serializers import CategorySerializer, PublicJobSerializer

from .models import Application, ApplicationStatusHistory


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStatusHistory
        fields = ("id", "previous_status", "new_status", "note", "created_at")
        read_only_fields = fields


class CandidateApplicationSerializer(serializers.ModelSerializer):
    job = PublicJobSerializer(read_only=True)
    cv = serializers.SerializerMethodField()
    status_history = ApplicationStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = ("id", "job", "cv", "cover_letter", "status", "applied_at", "updated_at", "status_history")
        read_only_fields = ("id", "job", "cv", "status", "applied_at", "updated_at", "status_history")

    @extend_schema_field(serializers.DictField())
    def get_cv(self, obj):
        return {"id": obj.cv_id, "original_filename": obj.cv.original_filename, "file_size": obj.cv.file_size, "status": obj.cv.status}


class CandidateApplicationCreateSerializer(serializers.Serializer):
    job_id = serializers.PrimaryKeyRelatedField(source="job", queryset=Job.objects.all())
    cv_id = serializers.PrimaryKeyRelatedField(source="cv", queryset=CandidateCV.objects.all())
    cover_letter = serializers.CharField(required=False, allow_blank=True, max_length=10000)

    def validate(self, attrs):
        request = self.context["request"]
        profile = getattr(request.user, "candidate_profile", None)
        if profile is None:
            raise serializers.ValidationError({"profile": ["Candidate profile chưa tồn tại."]})
        job = attrs["job"]
        if job.status != Job.Status.PUBLISHED or job.deadline < date.today():
            raise serializers.ValidationError({"job_id": ["Job không còn nhận hồ sơ."]})
        cv = attrs["cv"]
        if cv.candidate_id != profile.id:
            raise serializers.ValidationError({"cv_id": ["CV phải thuộc Candidate hiện tại."]})
        if cv.status != CandidateCV.Status.ACTIVE:
            raise serializers.ValidationError({"cv_id": ["CV không còn ở trạng thái sử dụng."]})
        if Application.objects.filter(job=job, candidate=profile).exists():
            raise serializers.ValidationError({"job_id": ["Candidate đã ứng tuyển Job này."]})
        attrs["candidate"] = profile
        return attrs


class EmployerApplicationSerializer(serializers.ModelSerializer):
    job = PublicJobSerializer(read_only=True)
    candidate = serializers.SerializerMethodField()
    cv = serializers.SerializerMethodField()
    status_history = ApplicationStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = ("id", "job", "candidate", "cv", "cover_letter", "status", "applied_at", "updated_at", "status_history")
        read_only_fields = fields

    @extend_schema_field(serializers.DictField())
    def get_candidate(self, obj):
        return {
            "id": obj.candidate_id,
            "full_name": obj.candidate.full_name or f"{obj.candidate.user.first_name} {obj.candidate.user.last_name}".strip() or obj.candidate.user.email,
            "email": obj.candidate.user.email,
            "phone": obj.candidate.phone,
            "location": obj.candidate.location,
            "summary": obj.candidate.summary,
        }

    @extend_schema_field(serializers.DictField())
    def get_cv(self, obj):
        return {"id": obj.cv_id, "original_filename": obj.cv.original_filename, "file_size": obj.cv.file_size, "download_path": f"/api/v1/employer/applications/{obj.id}/cv/download/"}


class EmployerApplicationTransitionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Application.Status.choices)
    note = serializers.CharField(required=False, allow_blank=True, max_length=2000)
