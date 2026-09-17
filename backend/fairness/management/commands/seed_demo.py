from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from fairness.models import Engineer, Incident, Severity


class Command(BaseCommand):
    help = "Seeds a demo rotation with an overloaded, a balanced, and an underloaded engineer."

    def handle(self, *args, **options):
        now = timezone.now()

        hank = Engineer.objects.get_or_create(
            email="hank@demo.co", defaults={"full_name": "Heavy Hank"}
        )[0]
        maya = Engineer.objects.get_or_create(
            email="maya@demo.co", defaults={"full_name": "Middle Maya"}
        )[0]
        liv = Engineer.objects.get_or_create(
            email="liv@demo.co", defaults={"full_name": "Light Liv"}
        )[0]

        for i in range(4):
            Incident.objects.get_or_create(
                engineer=hank,
                title=f"overnight sev1 outage #{i}",
                paged_at=now.replace(hour=3) - timedelta(days=i * 5),
                defaults={
                    "severity": Severity.SEV1,
                    "resolved_at": now.replace(hour=3) - timedelta(days=i * 5) + timedelta(hours=2),
                },
            )

        for i in range(2):
            Incident.objects.get_or_create(
                engineer=maya,
                title=f"business hours sev2 #{i}",
                paged_at=now.replace(hour=14) - timedelta(days=i * 10),
                defaults={
                    "severity": Severity.SEV2,
                    "resolved_at": now.replace(hour=14) - timedelta(days=i * 10) + timedelta(minutes=30),
                },
            )

        Incident.objects.get_or_create(
            engineer=liv,
            title="minor sev4 alert",
            paged_at=now.replace(hour=10) - timedelta(days=2),
            defaults={"severity": Severity.SEV4, "resolved_at": now.replace(hour=10) - timedelta(days=2) + timedelta(minutes=5)},
        )

        self.stdout.write(self.style.SUCCESS("Seeded demo engineers and incidents."))
