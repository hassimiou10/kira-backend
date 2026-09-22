from django.contrib import admin

from .models import EducationRecord


@admin.register(EducationRecord)
class EducationRecordAdmin(admin.ModelAdmin):
    list_display = (
        "institution",
        "degree",
        "field_of_study",
        "owner",
        "start_date",
        "end_date",
        "is_current",
    )
    list_filter = ("is_current", "institution")
    search_fields = ("institution", "degree", "field_of_study", "description")
