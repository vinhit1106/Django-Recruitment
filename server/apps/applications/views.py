from datetime import date

from django.db import IntegrityError, transaction
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils.text import get_valid_filename
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.candidates.models import CandidateCV
from apps.companies.models import Company
from apps.jobs.models import Job

from .models import Application, ApplicationStatusHistory
from .permissions import IsCandidate, IsEmployer
from .serializers import CandidateApplicationCreateSerializer, CandidateApplicationSerializer, EmployerApplicationSerializer, EmployerApplicationTransitionSerializer


EMPLOYER_TRANSITIONS = {
    Application.Status.SUBMITTED: {Application.Status.REVIEWING, Application.Status.REJECTED},
    Application.Status.REVIEWING: {Application.Status.SHORTLISTED, Application.Status.REJECTED},
    Application.Status.SHORTLISTED: {Application.Status.HIRED, Application.Status.REJECTED},
}
CANDIDATE_WITHDRAWABLE = {Application.Status.SUBMITTED, Application.Status.REVIEWING, Application.Status.SHORTLISTED}


def candidate_applications(request):
    profile = getattr(request.user, "candidate_profile", None)
    return Application.objects.filter(candidate=profile).select_related("job__company", "job__category", "cv").prefetch_related("status_history") if profile else Application.objects.none()


def employer_applications(request):
    return Application.objects.filter(job__company__owner=request.user).select_related("job__company", "job__category", "candidate", "cv").prefetch_related("status_history")


class CandidateApplicationListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsCandidate]

    def get_queryset(self):
        return candidate_applications(self.request)

    def get_serializer_class(self):
        return CandidateApplicationCreateSerializer if self.request.method == "POST" else CandidateApplicationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data
        try:
            with transaction.atomic():
                application = Application.objects.create(job=values["job"], candidate=values["candidate"], cv=values["cv"], cover_letter=values.get("cover_letter", ""))
                ApplicationStatusHistory.objects.create(application=application, previous_status="", new_status=application.status, changed_by=request.user, note="Application submitted")
        except IntegrityError as exc:
            return Response({"error": {"code": "DUPLICATE_APPLICATION", "message": "Candidate đã ứng tuyển Job này.", "details": {}}}, status=status.HTTP_409_CONFLICT)
        return Response(CandidateApplicationSerializer(application).data, status=status.HTTP_201_CREATED)


class CandidateApplicationDetailView(generics.RetrieveAPIView):
    permission_classes = [IsCandidate]
    serializer_class = CandidateApplicationSerializer

    def get_queryset(self):
        return candidate_applications(self.request)


class CandidateApplicationWithdrawView(APIView):
    permission_classes = [IsCandidate]
    serializer_class = CandidateApplicationSerializer

    def post(self, request, pk):
        application = get_object_or_404(candidate_applications(request), pk=pk)
        if application.status not in CANDIDATE_WITHDRAWABLE:
            return Response({"error": {"code": "INVALID_STATUS_TRANSITION", "message": "Application không thể rút ở trạng thái hiện tại.", "details": {}}}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            previous = application.status
            application.status = Application.Status.WITHDRAWN
            application.save(update_fields=["status", "updated_at"])
            ApplicationStatusHistory.objects.create(application=application, previous_status=previous, new_status=application.status, changed_by=request.user, note="Application withdrawn")
        return Response(CandidateApplicationSerializer(application).data)


class EmployerApplicationListView(generics.ListAPIView):
    permission_classes = [IsEmployer]
    serializer_class = EmployerApplicationSerializer

    def get_queryset(self):
        queryset = employer_applications(self.request)
        if self.request.query_params.get("status"):
            queryset = queryset.filter(status=self.request.query_params["status"])
        if self.request.query_params.get("job_id"):
            queryset = queryset.filter(job_id=self.request.query_params["job_id"])
        return queryset


class EmployerApplicationDetailView(generics.RetrieveAPIView):
    permission_classes = [IsEmployer]
    serializer_class = EmployerApplicationSerializer

    def get_queryset(self):
        return employer_applications(self.request)


class EmployerApplicationTransitionView(APIView):
    permission_classes = [IsEmployer]
    serializer_class = EmployerApplicationTransitionSerializer

    def post(self, request, pk):
        application = get_object_or_404(employer_applications(request), pk=pk)
        serializer = EmployerApplicationTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target = serializer.validated_data["status"]
        allowed = EMPLOYER_TRANSITIONS.get(application.status, set())
        if target not in allowed:
            return Response({"error": {"code": "INVALID_STATUS_TRANSITION", "message": "Chuyển trạng thái application không hợp lệ.", "details": {"current_status": application.status, "target_status": target}}}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            previous = application.status
            application.status = target
            application.save(update_fields=["status", "updated_at"])
            ApplicationStatusHistory.objects.create(application=application, previous_status=previous, new_status=target, changed_by=request.user, note=serializer.validated_data.get("note", ""))
        return Response(EmployerApplicationSerializer(application).data)


class EmployerApplicationCVDownloadView(generics.GenericAPIView):
    permission_classes = [IsEmployer]
    serializer_class = EmployerApplicationSerializer

    def get(self, request, pk):
        application = get_object_or_404(employer_applications(request), pk=pk)
        if not application.cv.file or not application.cv.file.storage.exists(application.cv.file.name):
            return Response({"error": {"code": "FILE_NOT_FOUND", "message": "Không tìm thấy file CV.", "details": {}}}, status=status.HTTP_404_NOT_FOUND)
        response = FileResponse(application.cv.file.open("rb"), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{get_valid_filename(application.cv.original_filename)}"'
        return response
