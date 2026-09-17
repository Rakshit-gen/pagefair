from django.contrib import admin

from .models import Engineer, Incident


@admin.register(Engineer)
class EngineerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email")
    search_fields = ("full_name", "email")


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ("title", "engineer", "severity", "paged_at", "resolved_at")
    list_filter = ("severity",)
