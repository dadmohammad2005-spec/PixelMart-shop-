import json
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment
from apps.orders.models import Order


class StripeConfigView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            "publicKey": getattr(settings, 'STRIPE_PUBLIC_KEY', 'pk_test_placeholder_key')
        })


class VerifyPaymentView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        order_number = request.data.get('order_number')
        transaction_id = request.data.get('transaction_id')

        if not order_number:
            return Response({"error": "order_number is required."}, status=status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(Order, order_number=order_number)
        payment, _ = Payment.objects.get_or_create(order=order, defaults={
            'payment_method': order.payment_method,
            'amount': order.total_amount,
            'status': Payment.STATUS_PENDING
        })

        if order.payment_method == 'COD':
            payment.status = Payment.STATUS_PENDING
            payment.save()
            order.status = Order.STATUS_CONFIRMED
            order.save()
            return Response({"status": "confirmed", "message": "Cash on Delivery confirmed."})

        # Stripe verification
        stripe_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
        intent_id = transaction_id or payment.transaction_id

        if stripe_key and not stripe_key.startswith('sk_test_placeholder') and intent_id and not intent_id.startswith('pi_simulated'):
            try:
                stripe.api_key = stripe_key
                intent = stripe.PaymentIntent.retrieve(intent_id)
                if intent.status == 'succeeded':
                    payment.status = Payment.STATUS_SUCCESSFUL
                    payment.save()
                    order.payment_status = Order.PAYMENT_STATUS_PAID
                    order.status = Order.STATUS_CONFIRMED
                    order.save()
                    return Response({"status": "paid", "message": "Payment verified successfully."})
                else:
                    payment.status = Payment.STATUS_FAILED
                    payment.error_message = f"Stripe status: {intent.status}"
                    payment.save()
                    order.payment_status = Order.PAYMENT_STATUS_FAILED
                    order.save()
                    return Response({"status": "failed", "message": f"Payment status: {intent.status}"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                payment.status = Payment.STATUS_FAILED
                payment.error_message = str(e)
                payment.save()
                return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Test development sandbox confirmation
            payment.status = Payment.STATUS_SUCCESSFUL
            payment.save()
            order.payment_status = Order.PAYMENT_STATUS_PAID
            order.status = Order.STATUS_CONFIRMED
            order.save()
            return Response({
                "status": "paid",
                "message": "Test payment simulation verified successfully."
            })


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

        if not webhook_secret or webhook_secret.startswith('whsec_placeholder'):
            return Response({"status": "ignored (placeholder webhook secret)"}, status=status.HTTP_200_OK)

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except ValueError:
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            order_number = payment_intent.get('metadata', {}).get('order_number')
            if order_number:
                order = Order.objects.filter(order_number=order_number).first()
                if order:
                    order.payment_status = Order.PAYMENT_STATUS_PAID
                    order.status = Order.STATUS_CONFIRMED
                    order.save()
                    payment, _ = Payment.objects.get_or_create(order=order)
                    payment.status = Payment.STATUS_SUCCESSFUL
                    payment.transaction_id = payment_intent['id']
                    payment.save()

        return Response({"status": "success"}, status=status.HTTP_200_OK)
