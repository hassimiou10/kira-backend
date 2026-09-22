from datetime import timedelta

import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Plan, Subscription, Transaction
from .serializers import (
    PlanSerializer,
    SubscriptionSerializer,
    TransactionSerializer,
)

stripe.api_key = settings.STRIPE_SECRET_KEY


def sync_premium_status(user):
    now = timezone.now()

    subscription = (
        Subscription.objects
        .filter(
            user=user,
            status=Subscription.STATUS_ACTIVE,
        )
        .select_related("plan")
        .filter(
            Q(ends_at__isnull=True) | Q(ends_at__gt=now)
        )
        .first()
    )

    is_premium = subscription is not None

    if user.is_premium != is_premium:
        user.is_premium = is_premium
        user.save(update_fields=["is_premium"])

    return subscription


class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [AllowAny]


class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscription = sync_premium_status(request.user)

        if not subscription:
            return Response({
                "is_premium": False,
                "subscription": None,
            })

        return Response({
            "is_premium": True,
            "subscription": SubscriptionSerializer(subscription).data,
        })


class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        subscription = (
            Subscription.objects
            .filter(
                user=request.user,
                status=Subscription.STATUS_ACTIVE,
            )
            .first()
        )

        if not subscription:
            sync_premium_status(request.user)

            return Response(
                {"error": "Aucun abonnement actif."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if subscription.stripe_subscription_id:
            try:
                stripe.Subscription.delete(
                    subscription.stripe_subscription_id
                )
            except Exception as e:
                return Response(
                    {"error": f"Erreur Stripe: {str(e)}"},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

        subscription.status = Subscription.STATUS_CANCELED
        subscription.canceled_at = timezone.now()
        subscription.save(
            update_fields=["status", "canceled_at"]
        )

        sync_premium_status(request.user)

        return Response({
            "message": "Abonnement annulé avec succès.",
            "is_premium": request.user.is_premium,
        })


class StripeCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get("plan_id")

        if not plan_id:
            return Response(
                {"error": "plan_id est obligatoire."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        plan = get_object_or_404(
            Plan,
            pk=plan_id,
            is_active=True,
        )

        existing_subscription = sync_premium_status(request.user)

        if existing_subscription:
            return Response(
                {
                    "error": "Vous avez déjà un abonnement Premium actif.",
                    "subscription": SubscriptionSerializer(
                        existing_subscription
                    ).data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        success_url = request.data.get(
            "success_url",
            "https://kira-app.com/#/payment/success",
        )

        cancel_url = request.data.get(
            "cancel_url",
            "https://kira-app.com/#/payment/cancel",
        )

        try:
            customer_id = request.user.stripe_customer_id

            if not customer_id:
                customer = stripe.Customer.create(
                    email=request.user.email or None,
                    name=(
                        request.user.get_full_name()
                        or request.user.username
                    ),
                    metadata={
                        "user_id": str(request.user.id),
                    },
                )

                customer_id = customer.id

                request.user.stripe_customer_id = customer_id
                request.user.save(
                    update_fields=["stripe_customer_id"]
                )

            checkout_session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": plan.name,
                            },
                            "unit_amount": int(
                                plan.price_usd * 100
                            ),
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "user_id": str(request.user.id),
                    "plan_id": str(plan.id),
                },
            )

        except Exception as e:
            return Response(
                {"error": f"Erreur Stripe: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        Transaction.objects.create(
            user=request.user,
            plan=plan,
            provider=Transaction.PROVIDER_STRIPE,
            status=Transaction.STATUS_PENDING,
            amount=plan.price_usd,
            currency="usd",
            provider_reference=checkout_session.id,
        )

        return Response({
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
        })


class StripeWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                webhook_secret,
            )
        except (
            ValueError,
            stripe.error.SignatureVerificationError,
        ):
            return Response(
                {"error": "Webhook Stripe invalide."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            self._handle_successful_payment(session)

        return Response(
            {"received": True},
            status=status.HTTP_200_OK,
        )

    def _handle_successful_payment(self, session):
        transaction = (
            Transaction.objects
            .select_related("user", "plan")
            .filter(
                provider_reference=session["id"]
            )
            .first()
        )

        if not transaction:
            return

        if transaction.status == Transaction.STATUS_SUCCESS:
            return

        transaction.status = Transaction.STATUS_SUCCESS
        transaction.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        if not transaction.plan:
            return

        existing_subscription = (
            Subscription.objects
            .filter(
                user=transaction.user,
                status=Subscription.STATUS_ACTIVE,
            )
            .first()
        )

        if existing_subscription:
            return

        stripe_customer_id = session.get("customer") or ""

        if stripe_customer_id:
            transaction.user.stripe_customer_id = stripe_customer_id
            transaction.user.save(
                update_fields=[
                    "stripe_customer_id",
                ]
            )

        Subscription.objects.create(
            user=transaction.user,
            plan=transaction.plan,
            status=Subscription.STATUS_ACTIVE,
            stripe_customer_id=stripe_customer_id,
            ends_at=(
                timezone.now()
                + timedelta(
                    days=transaction.plan.duration_days
                )
            ),
        )

        transaction.user.is_premium = True
        transaction.user.save(
            update_fields=[
                "is_premium",
            ]
        )


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(
            user=self.request.user
        )