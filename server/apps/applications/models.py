from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.candidates.models import CandidateCV, CandidateProfile
from apps.jobs.models import Job


class Application(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "SUBMITTED", "Submitted"
        REVIEWING = "REVIEWING", "Reviewing"
        SHORTLISTED = "SHORTLISTED", "Shortlisted"
        REJECTED = "REJECTED", "Rejected"
        HIRED = "HIRED", "Hired"
        WITHDRAWN = "WITHDRAWN", "Withdrawn"

    job = models.ForeignKey(Job, on_delete=models.PROTECT, related_name="applications")
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.PROTECT, related_name="applications")
    cv = models.ForeignKey(CandidateCV, on_delete=models.PROTECT, related_name="applications")
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    applied_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_at"]
        constraints = [models.UniqueConstraint(fields=["job", "candidate"], name="unique_job_candidate_application")]
        indexes = [
            models.Index(fields=["candidate", "status"], name="application_candidate_status"),
            models.Index(fields=["job", "status"], name="application_job_status"),
        ]

    def __str__(self):
        return f"{self.candidate} -> {self.job}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.cv_id and self.candidate_id and self.cv.candidate_id != self.candidate_id:
            raise ValidationError({"cv": "The selected CV must belong to the candidate."})


class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="status_history")
    previous_status = models.CharField(max_length=20, choices=Application.Status.choices, blank=True)
    new_status = models.CharField(max_length=20, choices=Application.Status.choices)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="application_status_changes")
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["created_at"]
        indexes = [models.Index(fields=["application", "created_at"], name="history_application_date")]
