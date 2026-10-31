from django.urls import path
from .views import (
    CartView,
    AddToCartView,
    UpdateCartItemView,
    ApplyCouponView,
)

urlpatterns = [
    path('', CartView.as_view(), name='cart-detail'),
    path('items/', AddToCartView.as_view(), name='cart-add-item'),
    path('items/<int:item_id>/', UpdateCartItemView.as_view(), name='cart-item-detail'),
    path('coupon/', ApplyCouponView.as_view(), name='cart-coupon'),
]
