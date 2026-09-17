from rest_framework import serializers

from .models import Engineer, Incident


class EngineerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Engineer
        fields = ["id", "full_name", "email"]


class IncidentSerializer(serializers.ModelSerializer):
    engineer_email = serializers.CharField(source="engineer.email", read_only=True)

    class Meta:
        model = Incident
        fields = [
            "id", "engineer", "engineer_email", "title", "severity",
            "paged_at", "acknowledged_at", "resolved_at",
        ]


class EngineerBurdenSerializer(serializers.Serializer):
    engineer_email = serializers.EmailField()
    engineer_name = serializers.CharField()
    incident_count = serializers.IntegerField()
    burden_score = serializers.FloatField()
    pct_of_team_average = serializers.FloatField()
    flag = serializers.CharField()
