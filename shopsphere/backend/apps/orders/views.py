import decimal
import stripe
from django.conf import settings
from django.db import models, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import Order, OrderItem
from .serializers import (
    OrderDetailSerializer,
    OrderListSerializer,
    CheckoutSerializer,
    OrderStatusUpdateSerializer,
)
from apps.cart.utils import get_or_create_cart
from apps.products.models import Product
from apps.promotions.models import Coupon, CouponUsage
from apps.payments.models import Payment
from apps.accounts.models import Address


class CheckoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        cart = get_or_create_cart(request)
        if cart.is_empty:
            return Response({"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            with transaction.atomic():
                # Lock products to prevent race conditions and check stock
                cart_items = cart.items.select_related('product').all()
                product_ids = [item.product.id for item in cart_items]
                locked_products = {
                    p.id: p
                    for p in Product.objects.select_for_update().filter(id__in=product_ids)
                }

                # Validate stock for all items first
                for item in cart_items:
                    product = locked_products.get(item.product.id)
                    if not product or not product.is_active:
                        raise ValueError(f"Product '{item.product.name}' is no longer available.")
                    if product.stock < item.quantity:
                        raise ValueError(f"Insufficient stock for '{product.name}'. Only {product.stock} available.")

                # Calculate verified totals
                subtotal = decimal.Decimal('0.00')
                for item in cart_items:
                    product = locked_products[item.product.id]
                    unit_price = product.current_price
                    subtotal += unit_price * item.quantity

                discount_amount = decimal.Decimal('0.00')
                applied_coupon = None
                if cart.coupon_code:
                    try:
                        coupon = Coupon.objects.select_for_update().get(code__iexact=cart.coupon_code, is_active=True)
                        valid, msg = coupon.validate_for_order(subtotal, user=request.user if request.user.is_authenticated else None)
                        if valid:
                            discount_amount = coupon.calculate_discount(subtotal)
                            applied_coupon = coupon
                    except Coupon.DoesNotExist:
                        pass

                shipping_rule = data.get('shipping_method', 'standard')
                if subtotal == 0:
                    shipping_cost = decimal.Decimal('0.00')
                elif shipping_rule == 'express':
                    shipping_cost = decimal.Decimal('19.99')
                elif subtotal >= decimal.Decimal('100.00'):
                    shipping_cost = decimal.Decimal('0.00')
                else:
                    shipping_cost = decimal.Decimal('9.99')

                total_amount = max(decimal.Decimal('0.00'), subtotal - discount_amount + shipping_cost)

                # Create Order record
                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    customer_email=data['customer_email'],
                    customer_name=data['customer_name'],
                    customer_phone=data['customer_phone'],
                    shipping_name=data['shipping_name'],
                    shipping_phone=data['shipping_phone'],
                    shipping_address_line1=data['shipping_address_line1'],
                    shipping_address_line2=data.get('shipping_address_line2', ''),
                    shipping_city=data['shipping_city'],
                    shipping_state=data['shipping_state'],
                    shipping_postal_code=data['shipping_postal_code'],
                    shipping_country=data.get('shipping_country', 'United States'),
                    shipping_method=shipping_rule,
                    subtotal=subtotal,
                    shipping_cost=shipping_cost,
                    discount_amount=discount_amount,
                    coupon_code=applied_coupon.code if applied_coupon else '',
                    total_amount=total_amount,
                    status=Order.STATUS_CONFIRMED if data['payment_method'] == 'COD' else Order.STATUS_PENDING,
                    payment_method=data['payment_method'],
                    payment_status=Order.PAYMENT_STATUS_PENDING,
                    order_notes=data.get('order_notes', '')
                )

                # Create OrderItems and deduct stock
                for item in cart_items:
                    product = locked_products[item.product.id]
                    unit_price = product.current_price
                    line_total = unit_price * item.quantity

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        product_sku=product.sku,
                        product_image_url=product.main_image.url if product.main_image else '',
                        price=unit_price,
                        quantity=item.quantity,
                        line_total=line_total
                    )

                    # Deduct stock safely
                    product.stock -= item.quantity
                    product.save(update_fields=['stock'])

                # Track coupon usage
                if applied_coupon:
                    applied_coupon.used_count += 1
                    applied_coupon.save(update_fields=['used_count'])
                    if request.user.is_authenticated:
                        CouponUsage.objects.create(
                            coupon=applied_coupon,
                            user=request.user,
                            order=order
                        )

                # Create Payment Record
                client_secret = ''
                transaction_id = ''
                payment_status = Payment.STATUS_PENDING

                if data['payment_method'] == 'STRIPE':
                    stripe_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
                    if stripe_key and not stripe_key.startswith('sk_test_placeholder'):
                        try:
                            stripe.api_key = stripe_key
                            intent = stripe.PaymentIntent.create(
                                amount=int(total_amount * 100),
                                currency='usd',
                                metadata={'order_number': order.order_number, 'order_id': order.id},
                                receipt_email=order.customer_email
                            )
                            client_secret = intent.client_secret
                            transaction_id = intent.id
                        except Exception as e:
                            # Payment initialization failure handled gracefully
                            payment_status = Payment.STATUS_FAILED
                            transaction_id = f"FAILED-{e}"
                    else:
                        # Test sandbox simulation for portfolio demonstration
                        transaction_id = f"pi_simulated_{order.order_number}"
                        client_secret = f"{transaction_id}_secret_demo"

                Payment.objects.create(
                    order=order,
                    payment_method=data['payment_method'],
                    amount=total_amount,
                    currency='usd',
                    status=payment_status,
                    transaction_id=transaction_id,
                    client_secret=client_secret
                )

                # Optionally save address for authenticated user
                if request.user.is_authenticated and data.get('save_address'):
                    Address.objects.get_or_create(
                        user=request.user,
                        address_line1=data['shipping_address_line1'],
                        city=data['shipping_city'],
                        defaults={
                            'full_name': data['shipping_name'],
                            'phone_number': data['shipping_phone'],
                            'address_line2': data.get('shipping_address_line2', ''),
                            'state': data['shipping_state'],
                            'postal_code': data['shipping_postal_code'],
                            'country': data.get('shipping_country', 'United States'),
                        }
                    )

                # Clear the cart after order is successfully recorded
                cart.items.all().delete()
                cart.coupon_code = ''
                cart.save()

                return Response({
                    "message": "Order created successfully.",
                    "order_number": order.order_number,
                    "order": OrderDetailSerializer(order).data,
                    "client_secret": client_secret,
                }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred during checkout: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserOrderListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number)

        # Secure authorization: Allow authenticated owner, staff, or guest email verification
        if request.user.is_authenticated:
            if order.user != request.user and not request.user.is_staff:
                return Response({"error": "You do not have permission to view this order."}, status=status.HTTP_403_FORBIDDEN)
        else:
            email_check = request.query_params.get('email')
            if not email_check or email_check.lower() != order.customer_email.lower():
                return Response({"error": "Please provide your billing email to view this guest order."}, status=status.HTTP_403_FORBIDDEN)

        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)


class OrderCancelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_number):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        if not order.can_cancel:
            return Response(
                {"error": f"Cannot cancel order in '{order.get_status_display()}' status."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Restore stock
            for item in order.items.select_related('product').all():
                if item.product:
                    Product.objects.filter(id=item.product.id).update(stock=models.F('stock') + item.quantity)

            order.status = Order.STATUS_CANCELLED
            order.save(update_fields=['status', 'updated_at'])

        return Response({"message": "Order has been successfully cancelled and inventory restored.", "order": OrderDetailSerializer(order).data})


class AdminOrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = OrderDetailSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'payment_method']
    search_fields = ['order_number', 'customer_name', 'customer_email', 'shipping_city']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        return Order.objects.all().prefetch_related('items', 'payment').select_related('user')

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            new_status = serializer.validated_data['status']
            order.status = new_status
            notes = serializer.validated_data.get('notes')
            if notes:
                order.order_notes = f"{order.order_notes}\n[Admin note: {notes}]"
            order.save()
            return Response({"message": f"Order status updated to {new_status}.", "order": OrderDetailSerializer(order).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
