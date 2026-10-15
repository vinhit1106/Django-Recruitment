from pathlib import Path
import sys
import tempfile
import os
from datetime import timedelta

from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() in {"1", "true", "yes", "on"}
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be set in the environment.")
if len(SECRET_KEY.encode("utf-8")) < 32 or len(set(SECRET_KEY)) < 5:
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must contain at least 32 bytes and sufficient entropy.")
ALLOWED_HOSTS = [host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if host.strip()]

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "corsheaders", "rest_framework", "drf_spectacular",
    "rest_framework_simplejwt.token_blacklist",
    "apps.accounts", "apps.candidates", "apps.companies", "apps.jobs", "apps.applications", "apps.adminapi",
    "apps.core",
]
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware", "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [], "APP_DIRS": True, "OPTIONS": {"context_processors": ["django.template.context_processors.request", "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {"default": {"ENGINE": "django.db.backends.postgresql", "NAME": os.getenv("DB_NAME", "recruitment"), "USER": os.getenv("DB_USER", "postgres"), "PASSWORD": os.getenv("DB_PASSWORD", ""), "HOST": os.getenv("DB_HOST", "localhost"), "PORT": os.getenv("DB_PORT", "5432"), "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "0"))}}
AUTH_PASSWORD_VALIDATORS = [{"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"}, {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"}, {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"}]
LANGUAGE_CODE = "en-us"
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "Asia/Ho_Chi_Minh")
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = Path(os.getenv("DJANGO_MEDIA_ROOT", str(BASE_DIR / "media")))
if "test" in sys.argv:
    MEDIA_ROOT = Path(tempfile.mkdtemp(prefix="ptit-careerhub-tests-"))
MAX_CV_UPLOAD_SIZE = int(os.getenv("MAX_CV_UPLOAD_SIZE", str(5 * 1024 * 1024)))
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv("DATA_UPLOAD_MAX_MEMORY_SIZE", str(MAX_CV_UPLOAD_SIZE + 1024 * 1024)))
FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.getenv("FILE_UPLOAD_MAX_MEMORY_SIZE", str(MAX_CV_UPLOAD_SIZE + 1024 * 1024)))
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "accounts.User"
REST_FRAMEWORK = {"DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework_simplejwt.authentication.JWTAuthentication",), "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",), "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema", "EXCEPTION_HANDLER": "apps.core.exceptions.api_exception_handler", "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination", "PAGE_SIZE": 20}
SIMPLE_JWT = {"ALGORITHM": "HS256", "SIGNING_KEY": SECRET_KEY, "VERIFYING_KEY": "", "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("ACCESS_TOKEN_LIFETIME_MINUTES", "30"))), "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("REFRESH_TOKEN_LIFETIME_DAYS", "7"))), "ROTATE_REFRESH_TOKENS": True, "BLACKLIST_AFTER_ROTATION": True, "AUTH_HEADER_TYPES": ("Bearer",)}
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",") if origin.strip()]
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "False").lower() == "true"
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()]
SPECTACULAR_SETTINGS = {"TITLE": "Django Recruitment API", "DESCRIPTION": "Versioned REST API for recruitment and candidate management.", "VERSION": "1.0.0", "SERVE_INCLUDE_SCHEMA": False, "ENUM_NAME_OVERRIDES": {"JobStatusEnum": "apps.jobs.models.Job.Status", "ApplicationStatusEnum": "apps.applications.models.Application.Status", "CVStatusEnum": "apps.candidates.models.CandidateCV.Status"}, "POSTPROCESSING_HOOKS": ["drf_spectacular.hooks.postprocess_schema_enums", "apps.core.schema.postprocess_registration_schema"]}
SPECTACULAR_SETTINGS["ENUM_NAME_OVERRIDES"].update({
    "UserRoleEnum": "apps.accounts.models.User.Role",
})
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "False").lower() == "true"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "False").lower() == "true"
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "False").lower() == "true"
SECURE_HSTS_PRELOAD = os.getenv("SECURE_HSTS_PRELOAD", "False").lower() == "true"
