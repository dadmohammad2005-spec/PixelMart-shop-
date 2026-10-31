from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from .utils import get_or_create_cart
from apps.products.models import Product
from apps.promotions.models import Coupon


class CartView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cart = get_or_create_cart(request)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)

    def delete(self, request):
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        cart.coupon_code = ''
        cart.save()
        return Response(
            {"message": "Cart cleared successfully.", "cart": CartSerializer(cart, context={'request': request}).data},
            status=status.HTTP_200_OK
        )


class AddToCartView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if quantity < 1:
            return Response({"error": "Quantity must be at least 1."}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id, is_active=True)

        if product.stock <= 0:
            return Response({"error": f"Sorry, '{product.name}' is currently out of stock."}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        new_quantity = quantity if created else cart_item.quantity + quantity

        if new_quantity > product.stock:
            return Response({
                "error": f"Cannot add {quantity} item(s). Only {product.stock} in stock (you already have {cart_item.quantity} in cart)."
            }, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = new_quantity
        cart_item.save()

        serializer = CartSerializer(cart, context={'request': request})
        return Response({
            "message": f"Added '{product.name}' to cart.",
            "cart": serializer.data
        }, status=status.HTTP_200_OK)


class UpdateCartItemView(APIView):
    permission_classes = [permissions.AllowAny]

    def put(self, request, item_id):
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        quantity = int(request.data.get('quantity', 1))

        if quantity < 1:
            return Response({"error": "Quantity must be at least 1. Use remove to delete item."}, status=status.HTTP_400_BAD_REQUEST)

        if quantity > cart_item.product.stock:
            return Response({
                "error": f"Requested {quantity} exceeds available stock of {cart_item.product.stock}."
            }, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartSerializer(cart, context={'request': request})
        return Response({
            "message": "Cart updated.",
            "cart": serializer.data
        }, status=status.HTTP_200_OK)

    def delete(self, request, item_id):
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        product_name = cart_item.product.name
        cart_item.delete()

        serializer = CartSerializer(cart, context={'request': request})
        return Response({
            "message": f"Removed '{product_name}' from cart.",
            "cart": serializer.data
        }, status=status.HTTP_200_OK)


class ApplyCouponView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        code = request.data.get('code', '').strip().upper()
        if not code:
            return Response({"error": "Please provide a coupon code."}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_or_create_cart(request)
        if cart.is_empty:
            return Response({"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            coupon = Coupon.objects.get(code__iexact=code, is_active=True)
        except Coupon.DoesNotExist:
            return Response({"error": "Invalid or inactive coupon code."}, status=status.HTTP_404_NOT_FOUND)

        valid, msg = coupon.validate_for_order(cart.subtotal, user=request.user if request.user.is_authenticated else None)
        if not valid:
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

        cart.coupon_code = coupon.code
        cart.save()

        serializer = CartSerializer(cart, context={'request': request})
        return Response({
            "message": f"Coupon '{coupon.code}' applied successfully!",
            "cart": serializer.data
        }, status=status.HTTP_200_OK)

    def delete(self, request):
        cart = get_or_create_cart(request)
        cart.coupon_code = ''
        cart.save()
        serializer = CartSerializer(cart, context={'request': request})
        return Response({
            "message": "Coupon removed.",
            "cart": serializer.data
        }, status=status.HTTP_200_OK)
