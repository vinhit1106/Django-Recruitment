from django.urls import path

from .views import CandidateApplicationDetailView, CandidateApplicationListCreateView, CandidateApplicationWithdrawView, EmployerApplicationCVDownloadView, EmployerApplicationDetailView, EmployerApplicationListView, EmployerApplicationTransitionView

urlpatterns = [
    path("candidate/applications/", CandidateApplicationListCreateView.as_view(), name="candidate-applications"),
    path("candidate/applications/<int:pk>/", CandidateApplicationDetailView.as_view(), name="candidate-application-detail"),
    path("candidate/applications/<int:pk>/withdraw/", CandidateApplicationWithdrawView.as_view(), name="candidate-application-withdraw"),
    path("employer/applications/", EmployerApplicationListView.as_view(), name="employer-applications"),
    path("employer/applications/<int:pk>/", EmployerApplicationDetailView.as_view(), name="employer-application-detail"),
    path("employer/applications/<int:pk>/transition/", EmployerApplicationTransitionView.as_view(), name="employer-application-transition"),
    path("employer/applications/<int:pk>/cv/download/", EmployerApplicationCVDownloadView.as_view(), name="employer-application-cv-download"),
]
