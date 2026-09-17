import csv
import io

from django.utils.dateparse import parse_datetime

from .models import Engineer, Incident


def _parse_dt(value: str):
    value = (value or "").strip()
    return parse_datetime(value) if value else None


def import_incidents_csv(file) -> int:
    """Upserts incidents from a CSV with columns:

    engineer_email, engineer_name, title, severity, paged_at, acknowledged_at, resolved_at

    `severity` is 1 (sev1, most severe) through 4. Engineers are created on
    first sight so this works as the only import step for a new team.
    """
    reader = csv.DictReader(io.TextIOWrapper(file, encoding="utf-8"))
    count = 0
    for row in reader:
        engineer, _ = Engineer.objects.get_or_create(
            email=row["engineer_email"].strip(),
            defaults={"full_name": row.get("engineer_name", "").strip()},
        )

        paged_at = _parse_dt(row.get("paged_at"))
        if paged_at is None:
            continue

        Incident.objects.update_or_create(
            engineer=engineer,
            title=row["title"].strip(),
            paged_at=paged_at,
            defaults={
                "severity": int(row.get("severity") or 3),
                "acknowledged_at": _parse_dt(row.get("acknowledged_at")),
                "resolved_at": _parse_dt(row.get("resolved_at")),
            },
        )
        count += 1
    return count
