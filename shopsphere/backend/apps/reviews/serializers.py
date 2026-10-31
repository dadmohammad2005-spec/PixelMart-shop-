from rest_framework import serializers
from .models import Review
from apps.products.models import Product
from apps.orders.models import OrderItem, Order


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'product', 'user_name', 'rating', 'title',
            'comment', 'is_verified_purchase', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'product', 'user_name', 'is_verified_purchase', 'created_at', 'updated_at']

    def get_user_name(self, obj):
        if obj.user:
            if obj.user.first_name:
                return f"{obj.user.first_name} {obj.user.last_name[:1]}." if obj.user.last_name else obj.user.first_name
            return obj.user.username
        return "Customer"


class ReviewCreateSerializer(serializers.ModelSerializer):
    product_slug = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Product.objects.filter(is_active=True),
        source='product'
    )

    class Meta:
        model = Review
        fields = ['product_slug', 'rating', 'title', 'comment']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be an integer between 1 and 5.")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        product = attrs['product']
        if Review.objects.filter(product=product, user=user).exists():
            raise serializers.ValidationError({"detail": "You have already submitted a review for this product."})
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data['product']

        # Determine if verified purchaser
        verified_purchase = OrderItem.objects.filter(
            order__user=user,
            order__status__in=[Order.STATUS_CONFIRMED, Order.STATUS_PROCESSING, Order.STATUS_SHIPPED, Order.STATUS_DELIVERED],
            product=product
        ).first()

        review = Review.objects.create(
            user=user,
            product=product,
            order=verified_purchase.order if verified_purchase else None,
            is_verified_purchase=bool(verified_purchase),
            rating=validated_data['rating'],
            title=validated_data['title'],
            comment=validated_data['comment'],
            is_approved=True
        )
        return review
