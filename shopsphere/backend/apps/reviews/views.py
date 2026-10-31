from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff and self.request.query_params.get('all') == 'true':
            qs = Review.objects.all()
        else:
            qs = Review.objects.filter(is_approved=True)

        product_slug = self.request.query_params.get('product')
        if product_slug:
            qs = qs.filter(product__slug=product_slug)

        return qs.select_related('user', 'product').order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ['create']:
            return ReviewCreateSerializer
        return ReviewSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_destroy(self, instance):
        if self.request.user.is_staff or instance.user == self.request.user:
            instance.delete()
        else:
            raise permissions.PermissionDenied("You do not have permission to delete this review.")

    @action(detail=False, methods=['get'])
    def homepage(self, request):
        """
        Returns recent approved customer reviews for homepage display.
        """
        reviews = self.get_queryset()[:6]
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def moderate(self, request, id=None):
        review = self.get_object()
        approved = request.data.get('is_approved', True)
        review.is_approved = approved
        review.save(update_fields=['is_approved'])
        return Response({"message": f"Review approval set to {approved}."})
