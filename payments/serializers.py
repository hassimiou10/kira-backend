from rest_framework import serializers

from .models import Plan, Subscription, Transaction


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            "id",
            "name",
            "description",
            "price_usd",
            "price_gnf",
            "duration_days",
            "is_active",
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "plan",
            "status",
            "started_at",
            "ends_at",
            "canceled_at",
        ]


class TransactionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "plan",
            "status",
            "amount",
            "currency",
            "provider",
            "provider_reference",
            "created_at",
        ]