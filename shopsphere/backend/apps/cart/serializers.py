from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.models import Product


class CartItemProductSerializer(serializers.ModelSerializer):
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'sku', 'price', 'sale_price', 'current_price', 'is_on_sale', 'main_image', 'stock']


class CartItemSerializer(serializers.ModelSerializer):
    product = CartItemProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source='product',
        write_only=True
    )
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    available_stock = serializers.IntegerField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'quantity',
            'unit_price', 'line_total', 'in_stock', 'available_stock'
        ]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    totals = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id', 'items', 'total_items', 'subtotal',
            'coupon_code', 'totals', 'is_empty', 'created_at', 'updated_at'
        ]

    def get_totals(self, obj):
        request = self.context.get('request')
        shipping_rule = 'standard'
        if request:
            shipping_rule = request.query_params.get('shipping_rule', 'standard')
        return obj.calculate_totals(shipping_rule=shipping_rule)
