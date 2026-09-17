from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from .models import Engineer, Incident, Severity
from .services import compute_fairness


class ComputeFairnessTests(TestCase):
    def setUp(self):
        self.now = timezone.now()

    def test_no_engineers_returns_empty(self):
        self.assertEqual(compute_fairness(), [])

    def test_engineer_with_no_recent_incidents_has_zero_burden(self):
        Engineer.objects.create(full_name="Idle Ivy", email="ivy@co.com")
        results = compute_fairness()
        self.assertEqual(results[0].burden_score, 0)
        self.assertEqual(results[0].flag, "balanced")

    def test_incidents_outside_window_are_ignored(self):
        eng = Engineer.objects.create(full_name="Old Oscar", email="oscar@co.com")
        Incident.objects.create(
            engineer=eng, title="stale sev1", severity=Severity.SEV1,
            paged_at=self.now - timedelta(days=200),
        )
        self.assertEqual(compute_fairness()[0].incident_count, 0)

    def test_off_hours_page_scores_double(self):
        eng = Engineer.objects.create(full_name="Night Nia", email="nia@co.com")
        day_paged = self.now.replace(hour=14)
        night_paged = self.now.replace(hour=3)

        day_eng = eng
        Incident.objects.create(
            engineer=day_eng, title="daytime sev2", severity=Severity.SEV2, paged_at=day_paged,
        )
        night_eng = Engineer.objects.create(full_name="Night Nia 2", email="nia2@co.com")
        Incident.objects.create(
            engineer=night_eng, title="overnight sev2", severity=Severity.SEV2, paged_at=night_paged,
        )

        results = {r.engineer_email: r for r in compute_fairness()}
        self.assertEqual(results["nia2@co.com"].burden_score, results["nia@co.com"].burden_score * 2)

    def test_overloaded_engineer_is_flagged(self):
        heavy = Engineer.objects.create(full_name="Heavy Hank", email="hank@co.com")
        light = Engineer.objects.create(full_name="Light Liv", email="liv@co.com")

        for _ in range(5):
            Incident.objects.create(
                engineer=heavy, title="sev1", severity=Severity.SEV1,
                paged_at=self.now.replace(hour=3),
            )
        Incident.objects.create(
            engineer=light, title="sev4", severity=Severity.SEV4, paged_at=self.now.replace(hour=14),
        )

        results = {r.engineer_email: r for r in compute_fairness()}
        self.assertEqual(results["hank@co.com"].flag, "overloaded")
        self.assertEqual(results["liv@co.com"].flag, "underloaded")

    def test_slow_resolution_adds_burden(self):
        eng = Engineer.objects.create(full_name="Slow Sal", email="sal@co.com")
        paged_at = self.now.replace(hour=14)
        Incident.objects.create(
            engineer=eng, title="slow sev3", severity=Severity.SEV3, paged_at=paged_at,
            resolved_at=paged_at + timedelta(hours=4),
        )
        # base weight 2, plus 4 hours * 0.5 = 2 more
        self.assertEqual(compute_fairness()[0].burden_score, 4.0)
