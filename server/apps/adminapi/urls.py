from django.urls import path

from .views import AdminApproveJobView, AdminCategoryDetailView, AdminCategoryListCreateView, AdminDashboardView, AdminPendingJobDetailView, AdminPendingJobListView, AdminRejectJobView, AdminSkillDetailView, AdminSkillListCreateView, AdminUserDetailView, AdminUserListView, CandidateDashboardView, EmployerDashboardView

urlpatterns = [
    path("admin/users/", AdminUserListView.as_view(), name="admin-users"),
    path("admin/users/<int:pk>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("admin/categories/", AdminCategoryListCreateView.as_view(), name="admin-categories"),
    path("admin/categories/<int:pk>/", AdminCategoryDetailView.as_view(), name="admin-category-detail"),
    path("admin/skills/", AdminSkillListCreateView.as_view(), name="admin-skills"),
    path("admin/skills/<int:pk>/", AdminSkillDetailView.as_view(), name="admin-skill-detail"),
    path("admin/jobs/pending/", AdminPendingJobListView.as_view(), name="admin-pending-jobs"),
    path("admin/jobs/pending/<int:pk>/", AdminPendingJobDetailView.as_view(), name="admin-pending-job-detail"),
    path("admin/jobs/<int:pk>/approve/", AdminApproveJobView.as_view(), name="admin-approve-job"),
    path("admin/jobs/<int:pk>/reject/", AdminRejectJobView.as_view(), name="admin-reject-job"),
    path("dashboard/candidate/", CandidateDashboardView.as_view(), name="candidate-dashboard"),
    path("employer/dashboard/", EmployerDashboardView.as_view(), name="employer-dashboard"),
    path("dashboard/employer/", EmployerDashboardView.as_view(), name="employer-dashboard-alias"),
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("dashboard/admin/", AdminDashboardView.as_view(), name="admin-dashboard-alias"),
]
