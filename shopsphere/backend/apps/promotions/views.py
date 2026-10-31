from decimal import Decimal
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Coupon, Announcement, NewsletterSubscriber
from .serializers import CouponSerializer, AnnouncementSerializer, NewsletterSerializer


class AnnouncementView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        announcement = Announcement.objects.filter(is_active=True).order_by('-updated_at').first()
        if announcement:
            return Response(AnnouncementSerializer(announcement).data)
        return Response({"message": "Welcome to Shall Shop — Discover More. Shop Better. Fast Shipping Worldwide!", "link_url": ""})


class NewsletterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        if not email or '@' not in email:
            return Response({"error": "Please enter a valid email address."}, status=status.HTTP_400_BAD_REQUEST)

        sub, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        if not sub.is_active:
            sub.is_active = True
            sub.save()

        return Response(
            {"message": "Thank you for subscribing to Shall Shop exclusive drops and VIP offers!"},
            status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED
        )


class CouponValidateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        code = request.data.get('code', '').strip().upper()
        subtotal_raw = request.data.get('subtotal', 0)
        try:
            subtotal = Decimal(str(subtotal_raw))
        except Exception:
            subtotal = Decimal('0.00')

        if not code:
            return Response({"error": "Coupon code is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            coupon = Coupon.objects.get(code__iexact=code, is_active=True)
        except Coupon.DoesNotExist:
            return Response({"error": "Invalid or expired coupon code."}, status=status.HTTP_404_NOT_FOUND)

        is_valid, msg = coupon.validate_for_order(subtotal, user=request.user if request.user.is_authenticated else None)
        if not is_valid:
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

        discount = coupon.calculate_discount(subtotal)
        return Response({
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_value": coupon.discount_value,
            "calculated_discount": discount,
            "message": "Coupon is valid."
        })


class CouponAdminViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all().order_by('-created_at')
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
