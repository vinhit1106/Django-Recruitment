from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.applications.models import Application
from apps.candidates.models import Skill
from apps.companies.models import Company
from apps.jobs.models import Category, Job

from .permissions import IsAdminRole
from .serializers import AdminCategorySerializer, AdminSkillSerializer, AdminUserSerializer, AdminUserUpdateSerializer, DashboardSerializer, ModerationJobSerializer, RejectJobSerializer


class AdminUserListView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminUserSerializer
    queryset = User.objects.all().order_by("id")

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get("role"):
            queryset = queryset.filter(role=self.request.query_params["role"])
        if self.request.query_params.get("is_active") in {"true", "false"}:
            queryset = queryset.filter(is_active=self.request.query_params["is_active"] == "true")
        return queryset


class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminRole]
    queryset = User.objects.all()

    def get_serializer_class(self):
        return AdminUserUpdateSerializer if self.request.method in {"PATCH", "PUT"} else AdminUserSerializer

    def update(self, request, *args, **kwargs):
        target = self.get_object()
        serializer = self.get_serializer(target, data=request.data, partial=request.method == "PATCH")
        serializer.is_valid(raise_exception=True)
        if target.role == User.Role.ADMIN and serializer.validated_data.get("is_active") is False:
            active_admins = User.objects.filter(role=User.Role.ADMIN, is_active=True).count()
            if active_admins <= 1:
                return Response({"error": {"code": "LAST_ADMIN_PROTECTED", "message": "Không thể khóa tài khoản Admin cuối cùng.", "details": {}}}, status=status.HTTP_409_CONFLICT)
        serializer.save()
        return Response(AdminUserSerializer(target).data)


class AdminCategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminCategorySerializer
    queryset = Category.objects.all()


class AdminCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminCategorySerializer
    queryset = Category.objects.all()

    def perform_destroy(self, instance):
        try:
            instance.delete()
        except ProtectedError as exc:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"category": ["Category đang được Job tham chiếu và không thể xóa."]}) from exc


class AdminSkillListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminSkillSerializer
    queryset = Skill.objects.all().order_by("name")

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(name__icontains=search)
        if self.request.query_params.get("is_active") in {"true", "false"}:
            queryset = queryset.filter(is_active=self.request.query_params["is_active"] == "true")
        return queryset


class AdminSkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = AdminSkillSerializer
    queryset = Skill.objects.all()

    def perform_destroy(self, instance):
        # Skills are referenced by candidate profiles, so deactivate instead of
        # deleting a skill already used in the system.
        if instance.candidate_skills.exists():
            instance.is_active = False
            instance.save(update_fields=["is_active"])
            return
        instance.delete()


class AdminPendingJobListView(generics.ListAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = ModerationJobSerializer
    queryset = Job.objects.filter(status=Job.Status.PENDING).select_related("company", "category", "reviewed_by")


class AdminPendingJobDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = ModerationJobSerializer
    queryset = Job.objects.filter(status=Job.Status.PENDING).select_related("company", "category", "reviewed_by")


class AdminApproveJobView(APIView):
    permission_classes = [IsAdminRole]
    serializer_class = ModerationJobSerializer

    def post(self, request, pk):
        with transaction.atomic():
            job = get_object_or_404(Job.objects.select_for_update(), pk=pk)
            if job.status != Job.Status.PENDING:
                return Response({"error": {"code": "INVALID_STATUS_TRANSITION", "message": "Chỉ Job đang chờ duyệt mới được approve.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
            job.status = Job.Status.PUBLISHED
            job.reviewed_by = request.user
            job.reviewed_at = timezone.now()
            job.published_at = timezone.now()
            job.rejection_reason = ""
            job.save(update_fields=["status", "reviewed_by", "reviewed_at", "published_at", "rejection_reason", "updated_at"])
        return Response(ModerationJobSerializer(job).data)


class AdminRejectJobView(APIView):
    permission_classes = [IsAdminRole]
    serializer_class = RejectJobSerializer

    def post(self, request, pk):
        serializer = RejectJobSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            job = get_object_or_404(Job.objects.select_for_update(), pk=pk)
            if job.status != Job.Status.PENDING:
                return Response({"error": {"code": "INVALID_STATUS_TRANSITION", "message": "Chỉ Job đang chờ duyệt mới được reject.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
            job.status = Job.Status.REJECTED
            job.reviewed_by = request.user
            job.reviewed_at = timezone.now()
            job.rejection_reason = serializer.validated_data["reason"]
            job.save(update_fields=["status", "reviewed_by", "reviewed_at", "rejection_reason", "updated_at"])
        return Response(ModerationJobSerializer(job).data)


def count_by_status(queryset, field, statuses):
    return {status_value: queryset.filter(**{field: status_value}).count() for status_value in statuses}


class CandidateDashboardView(APIView):
    permission_classes = []
    serializer_class = DashboardSerializer

    def get(self, request):
        if not request.user.is_authenticated or request.user.role != User.Role.CANDIDATE:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied()
        applications = Application.objects.filter(candidate__user=request.user)
        recent = applications.select_related("job", "job__company")[:5]
        return Response({"application_count": applications.count(), "applications_by_status": count_by_status(applications, "status", [value for value, _ in Application.Status.choices]), "recent_applications": [{"id": item.id, "job_id": item.job_id, "job_title": item.job.title, "company_name": item.job.company.name, "status": item.status, "applied_at": item.applied_at} for item in recent]})


class EmployerDashboardView(APIView):
    permission_classes = []
    serializer_class = DashboardSerializer

    def get(self, request):
        if not request.user.is_authenticated or request.user.role != User.Role.EMPLOYER:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied()
        company = Company.objects.filter(owner=request.user).first()
        if company is None:
            return Response({"error": {"code": "COMPANY_NOT_FOUND", "message": "Employer chưa có Company.", "details": {}}}, status=status.HTTP_404_NOT_FOUND)
        jobs = Job.objects.filter(company=company)
        applications = Application.objects.filter(job__company=company)
        recent = applications.select_related("job", "candidate").order_by("-applied_at")[:5]
        return Response({"company_id": company.id, "job_count": jobs.count(), "jobs_by_status": count_by_status(jobs, "status", [value for value, _ in Job.Status.choices]), "application_count": applications.count(), "applications_by_status": count_by_status(applications, "status", [value for value, _ in Application.Status.choices]), "recent_applications": [{"id": item.id, "job_id": item.job_id, "job_title": item.job.title, "candidate_id": item.candidate_id, "status": item.status, "applied_at": item.applied_at} for item in recent]})


class AdminDashboardView(APIView):
    permission_classes = [IsAdminRole]
    serializer_class = DashboardSerializer

    def get(self, request):
        return Response({"user_count": User.objects.count(), "users_by_role": count_by_status(User.objects.all(), "role", [value for value, _ in User.Role.choices]), "company_count": Company.objects.count(), "job_count": Job.objects.count(), "jobs_by_status": count_by_status(Job.objects.all(), "status", [value for value, _ in Job.Status.choices]), "pending_job_count": Job.objects.filter(status=Job.Status.PENDING).count(), "application_count": Application.objects.count(), "applications_by_status": count_by_status(Application.objects.all(), "status", [value for value, _ in Application.Status.choices])})
