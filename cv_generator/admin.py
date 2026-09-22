from django.contrib import admin
from .models import CV


@admin.register(CV)
class CVAdmin(admin.ModelAdmin):
	list_display = ("id", "full_name", "owner", "email", "created_at")
	readonly_fields = ("created_at", "updated_at")
	search_fields = ("full_name", "email", "owner__username")
