from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnnouncementView, NewsletterView, CouponValidateView, CouponAdminViewSet

router = DefaultRouter()
router.register(r'admin/coupons', CouponAdminViewSet, basename='admin-coupon')

urlpatterns = [
    path('announcement/', AnnouncementView.as_view(), name='active-announcement'),
    path('newsletter/', NewsletterView.as_view(), name='newsletter-subscribe'),
    path('validate-coupon/', CouponValidateView.as_view(), name='validate-coupon'),
    path('', include(router.urls)),
]
