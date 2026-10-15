from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Company
from .permissions import IsEmployer
from .serializers import CompanySerializer, PublicCompanySerializer


def company_duplicate_response():
    return Response({"error": {"code": "COMPANY_EXISTS", "message": "Employer đã có Company.", "details": {}}}, status=status.HTTP_409_CONFLICT)


class EmployerCompanyView(generics.GenericAPIView):
    serializer_class = CompanySerializer
    permission_classes = [IsEmployer]

    def get_object(self):
        return Company.objects.filter(owner=self.request.user).first()

    def get(self, request):
        company = self.get_object()
        if company is None:
            return Response({"error": {"code": "COMPANY_NOT_FOUND", "message": "Employer chưa có Company.", "details": {}}}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(company).data)

    def post(self, request):
        if self.get_object() is not None:
            return company_duplicate_response()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            company = serializer.save(owner=request.user)
        except IntegrityError as exc:
            return company_duplicate_response()
        return Response(self.get_serializer(company).data, status=status.HTTP_201_CREATED)

    def patch(self, request):
        company = self.get_object()
        if company is None:
            return Response({"error": {"code": "COMPANY_NOT_FOUND", "message": "Employer chưa có Company.", "details": {}}}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(company, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PublicCompanyListView(generics.ListAPIView):
    queryset = Company.objects.all()
    serializer_class = PublicCompanySerializer
    permission_classes = []


class PublicCompanyDetailView(generics.RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = PublicCompanySerializer
    permission_classes = []
