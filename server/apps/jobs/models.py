from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from apps.companies.models import Company
from apps.candidates.models import CandidateProfile


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=170, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Job(models.Model):
    class EmploymentType(models.TextChoices):
        FULL_TIME = "FULL_TIME", "Full time"
        PART_TIME = "PART_TIME", "Part time"
        CONTRACT = "CONTRACT", "Contract"
        INTERNSHIP = "INTERNSHIP", "Internship"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PENDING = "PENDING", "Pending review"
        PUBLISHED = "PUBLISHED", "Published"
        REJECTED = "REJECTED", "Rejected"
        CLOSED = "CLOSED", "Closed"

    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="jobs")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="jobs")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_jobs")
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    salary_currency = models.CharField(max_length=3, default="VND")
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    rejection_reason = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_jobs")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(condition=Q(salary_min__isnull=True) | Q(salary_min__gte=0), name="job_salary_min_nonnegative"),
            models.CheckConstraint(condition=Q(salary_max__isnull=True) | Q(salary_max__gte=0), name="job_salary_max_nonnegative"),
            models.CheckConstraint(condition=Q(salary_min__isnull=True) | Q(salary_max__isnull=True) | Q(salary_min__lte=F("salary_max")), name="job_salary_min_lte_max"),
        ]
        indexes = [
            models.Index(fields=["status", "deadline"], name="job_public_status_date"),
            models.Index(fields=["category", "status"], name="job_category_status"),
            models.Index(fields=["company", "status"], name="job_company_status"),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        from django.core.exceptions import ValidationError
        errors = {}
        if self.salary_min is not None and self.salary_min < 0:
            errors["salary_min"] = "Salary cannot be negative."
        if self.salary_max is not None and self.salary_max < 0:
            errors["salary_max"] = "Salary cannot be negative."
        if self.salary_min is not None and self.salary_max is not None and self.salary_min > self.salary_max:
            errors["salary_max"] = "Maximum salary must be greater than or equal to minimum salary."
        if errors:
            raise ValidationError(errors)
