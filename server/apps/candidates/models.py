from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone
from uuid import uuid4


def cv_upload_path(instance, filename):
    return f"cvs/{instance.candidate_id}/{uuid4().hex}.pdf"


class CandidateProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="candidate_profile")
    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name or self.user.email


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CandidateSkill(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="candidate_skills")
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT, related_name="candidate_skills")
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["skill__name"]
        constraints = [models.UniqueConstraint(fields=["candidate", "skill"], name="unique_candidate_skill")]
        indexes = [models.Index(fields=["candidate", "skill"], name="candidate_skill_lookup")]


class Experience(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="experiences")
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "-created_at"]
        constraints = [
            models.CheckConstraint(condition=Q(end_date__isnull=True) | Q(end_date__gte=F("start_date")), name="experience_end_after_start"),
            models.CheckConstraint(condition=Q(is_current=False) | Q(end_date__isnull=True), name="current_experience_has_no_end"),
        ]
        indexes = [models.Index(fields=["candidate", "-start_date"], name="experience_candidate_date")]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date cannot be before start date."})
        if self.is_current and self.end_date:
            raise ValidationError({"end_date": "Current experience cannot have an end date."})


class CandidateCV(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ARCHIVED = "ARCHIVED", "Archived"

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name="cvs")
    file = models.FileField(upload_to=cv_upload_path, validators=[FileExtensionValidator(["pdf"])])
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveBigIntegerField(default=0)
    content_type = models.CharField(max_length=100, default="application/pdf")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["candidate", "status"], name="cv_candidate_status")]

    def __str__(self):
        return self.original_filename
