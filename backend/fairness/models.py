from django.db import models


class Severity(models.IntegerChoices):
    SEV1 = 1, "Sev1 - critical"
    SEV2 = 2, "Sev2 - major"
    SEV3 = 3, "Sev3 - minor"
    SEV4 = 4, "Sev4 - informational"

# Weight applied per severity when computing burden. Lower sev number = more weight.
SEVERITY_WEIGHT = {
    Severity.SEV1: 8,
    Severity.SEV2: 4,
    Severity.SEV3: 2,
    Severity.SEV4: 1,
}

OFF_HOURS_MULTIPLIER = 2  # paged between 22:00 and 07:00 UTC


class Engineer(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.full_name


class Incident(models.Model):
    engineer = models.ForeignKey(Engineer, on_delete=models.CASCADE, related_name="incidents")
    title = models.CharField(max_length=200)
    severity = models.IntegerField(choices=Severity.choices, default=Severity.SEV3)
    paged_at = models.DateTimeField()
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-paged_at"]

    def __str__(self):
        return f"{self.title} ({self.engineer.email})"

    @property
    def is_off_hours(self) -> bool:
        hour = self.paged_at.hour
        return hour >= 22 or hour < 7

    @property
    def resolution_minutes(self) -> float | None:
        if self.resolved_at is None:
            return None
        return (self.resolved_at - self.paged_at).total_seconds() / 60
