from dataclasses import dataclass
from datetime import timedelta

from django.utils import timezone

from .models import OFF_HOURS_MULTIPLIER, SEVERITY_WEIGHT, Engineer

WINDOW_DAYS = 90
OVERLOADED_RATIO = 1.5
UNDERLOADED_RATIO = 0.5
# Half a burden point per resolution-hour, so a slow sev-1 outweighs a fast one.
RESOLUTION_HOUR_WEIGHT = 0.5


@dataclass
class EngineerBurden:
    engineer_email: str
    engineer_name: str
    incident_count: int
    burden_score: float
    pct_of_team_average: float
    flag: str  # "overloaded", "underloaded", or "balanced"


def _incident_burden(incident) -> float:
    score = SEVERITY_WEIGHT[incident.severity]
    if incident.is_off_hours:
        score *= OFF_HOURS_MULTIPLIER
    resolution_minutes = incident.resolution_minutes
    if resolution_minutes:
        score += (resolution_minutes / 60) * RESOLUTION_HOUR_WEIGHT
    return score


def compute_fairness(window_days: int = WINDOW_DAYS) -> list[EngineerBurden]:
    """Per-engineer burden over the trailing window, flagged against the team average."""
    since = timezone.now() - timedelta(days=window_days)

    raw = []
    for engineer in Engineer.objects.prefetch_related("incidents"):
        incidents = [i for i in engineer.incidents.all() if i.paged_at >= since]
        burden = sum(_incident_burden(i) for i in incidents)
        raw.append((engineer, len(incidents), burden))

    if not raw:
        return []

    team_average = sum(b for _, _, b in raw) / len(raw)

    results = []
    for engineer, count, burden in raw:
        pct = (burden / team_average * 100) if team_average else 0.0
        if team_average and burden >= team_average * OVERLOADED_RATIO:
            flag = "overloaded"
        elif team_average and burden <= team_average * UNDERLOADED_RATIO:
            flag = "underloaded"
        else:
            flag = "balanced"
        results.append(
            EngineerBurden(
                engineer_email=engineer.email,
                engineer_name=engineer.full_name,
                incident_count=count,
                burden_score=round(burden, 2),
                pct_of_team_average=round(pct, 1),
                flag=flag,
            )
        )

    results.sort(key=lambda r: r.burden_score, reverse=True)
    return results
