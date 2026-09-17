import csv

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .importers import import_incidents_csv
from .models import Engineer, Incident
from .serializers import EngineerBurdenSerializer, EngineerSerializer, IncidentSerializer
from .services import WINDOW_DAYS, compute_fairness


class EngineerViewSet(viewsets.ModelViewSet):
    queryset = Engineer.objects.all().order_by("full_name")
    serializer_class = EngineerSerializer


class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.select_related("engineer").all()
    serializer_class = IncidentSerializer


class FairnessView(APIView):
    def get(self, request):
        window_days = int(request.query_params.get("window_days", WINDOW_DAYS))
        report = compute_fairness(window_days=window_days)
        return Response(EngineerBurdenSerializer(report, many=True).data)


class FairnessCsvView(APIView):
    """Downloadable copy of the fairness report, for pasting into a rotation review doc."""

    def get(self, request):
        window_days = int(request.query_params.get("window_days", WINDOW_DAYS))
        report = compute_fairness(window_days=window_days)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="pagefair_fairness_report.csv"'

        writer = csv.writer(response)
        writer.writerow(
            ["engineer_email", "engineer_name", "incident_count", "burden_score", "pct_of_team_average", "flag"]
        )
        for r in report:
            writer.writerow(
                [r.engineer_email, r.engineer_name, r.incident_count, r.burden_score, r.pct_of_team_average, r.flag]
            )
        return response


class ImportIncidentsView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        count = import_incidents_csv(request.FILES["file"])
        return Response({"imported": count})
