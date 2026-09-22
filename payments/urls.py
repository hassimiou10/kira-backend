from django.urls import path
from .views import (
    PlanListView,
    SubscriptionView,
    CancelSubscriptionView,
    StripeCheckoutView,
    StripeWebhookView,
    TransactionListView,
)

# La variable DOIT être nommée "urlpatterns" en minuscules
urlpatterns = [
    path("plans/", PlanListView.as_view(), name="payments-plans"),
    path("subscription/", SubscriptionView.as_view(), name="payments-subscription"),
    path("subscription/cancel/", CancelSubscriptionView.as_view(), name="payments-cancel"),
    path("stripe/checkout/", StripeCheckoutView.as_view(), name="payments-stripe-checkout"),
    path("stripe/webhook/", StripeWebhookView.as_view(), name="payments-stripe-webhook"),
    path("transactions/", TransactionListView.as_view(), name="payments-transactions"),
]