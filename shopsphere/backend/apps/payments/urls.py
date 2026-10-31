from django.urls import path
from .views import StripeConfigView, VerifyPaymentView, StripeWebhookView

urlpatterns = [
    path('config/', StripeConfigView.as_view(), name='payment-config'),
    path('verify/', VerifyPaymentView.as_view(), name='payment-verify'),
    path('webhook/', StripeWebhookView.as_view(), name='payment-webhook'),
]
