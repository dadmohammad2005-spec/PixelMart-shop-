from rest_framework import serializers
from .models import Order, OrderItem
from apps.payments.models import Payment


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'product_image_url', 'price', 'quantity', 'line_total'
        ]


class PaymentSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'payment_method', 'amount', 'currency', 'status', 'transaction_id', 'created_at']


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payment = PaymentSummarySerializer(read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status', 'payment_method',
            'customer_name', 'customer_email', 'customer_phone',
            'shipping_name', 'shipping_phone', 'shipping_address_line1',
            'shipping_address_line2', 'shipping_city', 'shipping_state',
            'shipping_postal_code', 'shipping_country', 'shipping_method',
            'subtotal', 'shipping_cost', 'discount_amount', 'coupon_code',
            'total_amount', 'total_items', 'can_cancel', 'order_notes',
            'items', 'payment', 'created_at', 'updated_at'
        ]


class OrderListSerializer(serializers.ModelSerializer):
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'payment_status', 'payment_method',
            'total_amount', 'total_items', 'created_at'
        ]


class CheckoutSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=150)
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField(max_length=30)

    shipping_name = serializers.CharField(max_length=150)
    shipping_phone = serializers.CharField(max_length=30)
    shipping_address_line1 = serializers.CharField(max_length=255)
    shipping_address_line2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    shipping_city = serializers.CharField(max_length=100)
    shipping_state = serializers.CharField(max_length=100)
    shipping_postal_code = serializers.CharField(max_length=20)
    shipping_country = serializers.CharField(max_length=100, default='United States')

    shipping_method = serializers.ChoiceField(choices=['standard', 'express'], default='standard')
    payment_method = serializers.ChoiceField(choices=['COD', 'STRIPE'], default='COD')
    order_notes = serializers.CharField(required=False, allow_blank=True)
    save_address = serializers.BooleanField(default=False, required=False)


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
