from django.urls import path

from .views import EmployerCompanyView, PublicCompanyDetailView, PublicCompanyListView

urlpatterns = [
    path("employer/company/", EmployerCompanyView.as_view(), name="employer-company"),
    path("companies/", PublicCompanyListView.as_view(), name="public-companies"),
    path("companies/<int:pk>/", PublicCompanyDetailView.as_view(), name="public-company-detail"),
]
