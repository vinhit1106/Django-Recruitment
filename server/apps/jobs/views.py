from datetime import date
from decimal import Decimal, InvalidOperation

from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.companies.models import Company

from .models import Category, Job
from .permissions import IsEmployer
from .serializers import CategorySerializer, EmployerJobSerializer, PublicJobSerializer


def public_queryset():
    return Job.objects.filter(status=Job.Status.PUBLISHED, deadline__gte=date.today()).select_related("company", "category")


def company_for(request):
    return Company.objects.filter(owner=request.user).first()


class PublicCategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = []
    queryset = Category.objects.filter(is_active=True).order_by("name")


class PublicJobListView(generics.ListAPIView):
    serializer_class = PublicJobSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = public_queryset()
        params = self.request.query_params
        search = params.get("search")
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search) | Q(requirements__icontains=search))
        if params.get("location"):
            queryset = queryset.filter(location__icontains=params["location"])
        if params.get("category"):
            queryset = queryset.filter(Q(category__slug=params["category"]) | Q(category__name__iexact=params["category"]))
        if params.get("employment_type"):
            queryset = queryset.filter(employment_type=params["employment_type"])
        try:
            if params.get("salary_min"):
                queryset = queryset.filter(salary_max__gte=Decimal(params["salary_min"]))
            if params.get("salary_max"):
                queryset = queryset.filter(salary_min__lte=Decimal(params["salary_max"]))
        except InvalidOperation:
            return Job.objects.none()
        ordering = params.get("ordering", "-created_at")
        allowed = {"created_at", "-created_at", "deadline", "-deadline", "salary_min", "-salary_min"}
        if ordering in allowed:
            queryset = queryset.order_by(ordering)
        return queryset


class PublicJobDetailView(generics.RetrieveAPIView):
    serializer_class = PublicJobSerializer
    permission_classes = []

    def get_queryset(self):
        return public_queryset()


class EmployerJobListCreateView(generics.ListCreateAPIView):
    serializer_class = EmployerJobSerializer
    permission_classes = [IsEmployer]

    def get_queryset(self):
        company = company_for(self.request)
        return Job.objects.filter(company=company).select_related("company", "category") if company else Job.objects.none()

    def create(self, request, *args, **kwargs):
        if company_for(request) is None:
            return Response({"error": {"code": "COMPANY_REQUIRED", "message": "Employer phải tạo Company trước khi đăng Job.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = serializer.save(company=company_for(request), created_by=request.user, status=Job.Status.DRAFT)
        return Response(self.get_serializer(job).data, status=status.HTTP_201_CREATED)


class EmployerJobDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployerJobSerializer
    permission_classes = [IsEmployer]

    def get_queryset(self):
        company = company_for(self.request)
        return Job.objects.filter(company=company).select_related("company", "category") if company else Job.objects.none()


class EmployerJobSubmitView(APIView):
    permission_classes = [IsEmployer]
    serializer_class = EmployerJobSerializer

    @extend_schema(request=None, responses=EmployerJobSerializer)
    def post(self, request, pk):
        job = generics.get_object_or_404(Job.objects.filter(company__owner=request.user), pk=pk)
        if job.status not in {Job.Status.DRAFT, Job.Status.REJECTED}:
            return Response({"error": {"code": "INVALID_STATUS_TRANSITION", "message": "Job không thể gửi duyệt ở trạng thái hiện tại.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
        job.status = Job.Status.PENDING
        job.rejection_reason = ""
        job.save(update_fields=["status", "rejection_reason", "updated_at"])
        return Response(EmployerJobSerializer(job).data)


class EmployerJobCloseView(APIView):
    permission_classes = [IsEmployer]
    serializer_class = EmployerJobSerializer

    @extend_schema(request=None, responses=EmployerJobSerializer)
    def post(self, request, pk):
        job = generics.get_object_or_404(Job.objects.filter(company__owner=request.user), pk=pk)
        if job.status == Job.Status.CLOSED:
            return Response(EmployerJobSerializer(job).data)
        job.status = Job.Status.CLOSED
        job.save(update_fields=["status", "updated_at"])
        return Response(EmployerJobSerializer(job).data)
