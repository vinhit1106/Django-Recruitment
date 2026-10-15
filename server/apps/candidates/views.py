from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ProtectedError
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils.text import get_valid_filename
from rest_framework import generics, status
from rest_framework.response import Response
from .models import CandidateCV, CandidateProfile, CandidateSkill, Experience, Skill
from .permissions import IsCandidate
from .serializers import CandidateCVSerializer, CandidateProfileSerializer, CandidateSkillSerializer, ExperienceSerializer, SkillSerializer

class PublicSkillListView(generics.ListAPIView):
    serializer_class = SkillSerializer
    permission_classes = []
    queryset = Skill.objects.filter(is_active=True).order_by("name")

def profile_for(request):
    try: return request.user.candidate_profile
    except ObjectDoesNotExist: return None
def missing_profile():
    return Response({"error": {"code": "PROFILE_NOT_FOUND", "message": "Candidate profile chưa tồn tại.", "details": {}}}, status=status.HTTP_404_NOT_FOUND)

class CandidateProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CandidateProfileSerializer; permission_classes = [IsCandidate]; http_method_names = ["get", "patch", "head", "options"]
    def get_object(self):
        profile = profile_for(self.request)
        if profile is None:
            from rest_framework.exceptions import NotFound
            raise NotFound("Candidate profile chưa tồn tại.")
        return profile

class CandidateSkillListCreateView(generics.ListCreateAPIView):
    serializer_class = CandidateSkillSerializer; permission_classes = [IsCandidate]
    def get_queryset(self):
        profile = profile_for(self.request); return CandidateSkill.objects.filter(candidate=profile).select_related("skill") if profile else CandidateSkill.objects.none()
    def create(self, request, *args, **kwargs):
        if profile_for(request) is None: return missing_profile()
        return super().create(request, *args, **kwargs)

class CandidateSkillDeleteView(generics.DestroyAPIView):
    serializer_class = CandidateSkillSerializer; permission_classes = [IsCandidate]
    def get_queryset(self):
        profile = profile_for(self.request); return CandidateSkill.objects.filter(candidate=profile) if profile else CandidateSkill.objects.none()

class ExperienceListCreateView(generics.ListCreateAPIView):
    serializer_class = ExperienceSerializer; permission_classes = [IsCandidate]
    def get_queryset(self):
        profile = profile_for(self.request); return Experience.objects.filter(candidate=profile) if profile else Experience.objects.none()
    def create(self, request, *args, **kwargs):
        if profile_for(request) is None: return missing_profile()
        return super().create(request, *args, **kwargs)

class ExperienceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExperienceSerializer; permission_classes = [IsCandidate]
    def get_queryset(self):
        profile = profile_for(self.request); return Experience.objects.filter(candidate=profile) if profile else Experience.objects.none()

class CandidateCVListCreateView(generics.ListCreateAPIView):
    serializer_class = CandidateCVSerializer; permission_classes = [IsCandidate]
    def get_queryset(self):
        profile = profile_for(self.request); return CandidateCV.objects.filter(candidate=profile) if profile else CandidateCV.objects.none()
    def create(self, request, *args, **kwargs):
        if profile_for(request) is None: return missing_profile()
        return super().create(request, *args, **kwargs)

class CandidateCVDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CandidateCVSerializer; permission_classes = [IsCandidate]; http_method_names = ["get", "patch", "delete", "head", "options"]
    def get_queryset(self):
        profile = profile_for(self.request); return CandidateCV.objects.filter(candidate=profile) if profile else CandidateCV.objects.none()
    def perform_destroy(self, instance):
        file = instance.file
        try: instance.delete()
        except ProtectedError as exc:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"code": "CV_IN_USE", "message": "CV đang được hồ sơ ứng tuyển tham chiếu.", "details": {}}) from exc
        if file:
            file.delete(save=False)

class CandidateCVDownloadView(generics.GenericAPIView):
    serializer_class = CandidateCVSerializer
    permission_classes = [IsCandidate]
    def get_queryset(self):
        profile = profile_for(self.request); return CandidateCV.objects.filter(candidate=profile) if profile else CandidateCV.objects.none()
    def get(self, request, pk):
        cv = get_object_or_404(self.get_queryset(), pk=pk)
        if not cv.file or not cv.file.storage.exists(cv.file.name):
            return Response({"error": {"code": "FILE_NOT_FOUND", "message": "Không tìm thấy file CV.", "details": {}}}, status=status.HTTP_404_NOT_FOUND)
        response = FileResponse(cv.file.open("rb"), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{get_valid_filename(cv.original_filename)}"'
        return response
