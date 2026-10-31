from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WishlistItem
from .serializers import WishlistItemSerializer
from apps.products.models import Product
from apps.cart.models import CartItem
from apps.cart.utils import get_or_create_cart


class WishlistView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        items = WishlistItem.objects.filter(
            user=request.user,
            product__is_active=True
        ).select_related('product', 'product__category')
        serializer = WishlistItemSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({"error": "product_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id, is_active=True)
        wishlist_item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)

        if not created:
            # Toggle behavior: if already in wishlist and requested toggle, or return message
            if request.data.get('toggle'):
                wishlist_item.delete()
                return Response({"message": f"Removed '{product.name}' from wishlist.", "in_wishlist": False}, status=status.HTTP_200_OK)
            return Response({"message": f"'{product.name}' is already in your wishlist.", "in_wishlist": True}, status=status.HTTP_200_OK)

        return Response({"message": f"Added '{product.name}' to wishlist.", "in_wishlist": True}, status=status.HTTP_201_CREATED)


class WishlistItemDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, product_id):
        deleted_count, _ = WishlistItem.objects.filter(user=request.user, product_id=product_id).delete()
        if deleted_count > 0:
            return Response({"message": "Product removed from wishlist."}, status=status.HTTP_200_OK)
        return Response({"error": "Item not found in wishlist."}, status=status.HTTP_404_NOT_FOUND)


class MoveToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_active=True)

        if product.stock <= 0:
            return Response({"error": f"'{product.name}' is currently out of stock."}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
        else:
            cart_item.quantity = 1
            cart_item.save()

        # Remove from wishlist
        WishlistItem.objects.filter(user=request.user, product=product).delete()

        return Response({"message": f"Moved '{product.name}' to shopping cart."})
