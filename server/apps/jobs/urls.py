from django.urls import path

from .views import EmployerJobCloseView, EmployerJobDetailView, EmployerJobListCreateView, EmployerJobSubmitView, PublicCategoryListView, PublicJobDetailView, PublicJobListView

urlpatterns = [
    path("categories/", PublicCategoryListView.as_view(), name="public-categories"),
    path("jobs/", PublicJobListView.as_view(), name="public-jobs"),
    path("jobs/<int:pk>/", PublicJobDetailView.as_view(), name="public-job-detail"),
    path("employer/jobs/", EmployerJobListCreateView.as_view(), name="employer-jobs"),
    path("employer/jobs/<int:pk>/", EmployerJobDetailView.as_view(), name="employer-job-detail"),
    path("employer/jobs/<int:pk>/submit/", EmployerJobSubmitView.as_view(), name="employer-job-submit"),
    path("employer/jobs/<int:pk>/close/", EmployerJobCloseView.as_view(), name="employer-job-close"),
]
