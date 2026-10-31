from django.urls import path
from .views import WishlistView, WishlistItemDetailView, MoveToCartView

urlpatterns = [
    path('', WishlistView.as_view(), name='wishlist-list-create'),
    path('<int:product_id>/', WishlistItemDetailView.as_view(), name='wishlist-item-detail'),
    path('<int:product_id>/move-to-cart/', MoveToCartView.as_view(), name='wishlist-move-to-cart'),
]
