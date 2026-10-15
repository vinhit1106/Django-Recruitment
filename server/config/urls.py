from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [path("admin/", admin.site.urls), path("api/v1/", include("apps.core.urls")), path("api/v1/auth/", include("apps.accounts.urls")), path("api/v1/candidate/", include("apps.candidates.urls")), path("api/v1/", include("apps.companies.urls")), path("api/v1/", include("apps.jobs.urls")), path("api/v1/", include("apps.applications.urls")), path("api/v1/", include("apps.adminapi.urls")), path("api/schema/", SpectacularAPIView.as_view(), name="schema"), path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui")]
