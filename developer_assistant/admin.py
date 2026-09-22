from django.contrib import admin

from .models import DeveloperAssistantPrompt


@admin.register(DeveloperAssistantPrompt)
class DeveloperAssistantPromptAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "prompt", "response")
