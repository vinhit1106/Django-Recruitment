from django.conf import settings
from django.db import models
from django.utils import timezone


class Company(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="company")
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["name"], name="company_name_lookup")]

    def __str__(self):
        return self.name
