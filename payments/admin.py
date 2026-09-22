from django.contrib import admin
from .models import Plan, Subscription, Transaction


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price_usd", "price_gnf", "duration_days", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status", "started_at", "ends_at")
    list_filter = ("status", "plan")
    search_fields = ("user__username", "user__email", "stripe_subscription_id")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "provider", "amount", "currency", "status", "created_at")
    list_filter = ("status", "provider", "currency")
    search_fields = ("user__username", "user__email", "provider_reference")