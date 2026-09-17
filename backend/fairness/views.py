from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .importers import import_incidents_csv
from .models import Engineer, Incident
from .serializers import EngineerBurdenSerializer, EngineerSerializer, IncidentSerializer
from .services import compute_fairness


class EngineerViewSet(viewsets.ModelViewSet):
    queryset = Engineer.objects.all().order_by("full_name")
    serializer_class = EngineerSerializer


class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.select_related("engineer").all()
    serializer_class = IncidentSerializer


class FairnessView(APIView):
    def get(self, request):
        report = compute_fairness()
        return Response(EngineerBurdenSerializer(report, many=True).data)


class ImportIncidentsView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        count = import_incidents_csv(request.FILES["file"])
        return Response({"imported": count})
