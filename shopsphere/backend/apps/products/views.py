from django.db.models import Avg, Sum, Q
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
import django_filters

from .models import Category, Product, ProductImage
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductWriteSerializer,
    ProductImageSerializer,
)


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    category = django_filters.CharFilter(method='filter_category')
    brand = django_filters.CharFilter(field_name='brand', lookup_expr='iexact')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['is_featured', 'category', 'brand']

    def filter_category(self, queryset, name, value):
        if value:
            if value.isdigit():
                return queryset.filter(category_id=value)
            return queryset.filter(category__slug=value)
        return queryset

    def filter_in_stock(self, queryset, name, value):
        if value is True:
            return queryset.filter(stock__gt=0)
        elif value is False:
            return queryset.filter(stock=0)
        return queryset


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True).order_by('name')
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    pagination_class = None

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class ProductViewSet(viewsets.ModelViewSet):
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'brand', 'specs', 'short_description', 'description', 'sku', 'category__name']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        user = self.request.user
        # Staff can view inactive products in admin; public gets only active
        if user.is_authenticated and user.is_staff and self.request.query_params.get('all') == 'true':
            qs = Product.objects.all()
        else:
            qs = Product.objects.filter(is_active=True)

        qs = qs.select_related('category').prefetch_related('images', 'reviews')
        return qs

    def filter_queryset(self, queryset):
        # Apply custom sort translations before or overriding default ordering filter
        sort = self.request.query_params.get('sort')
        if sort in ['price_asc', 'price_desc', 'newest', 'rating', 'bestseller']:
            # Run other filters (django-filter and search)
            for backend in self.filter_backends:
                if backend != filters.OrderingFilter:
                    queryset = backend().filter_queryset(self.request, queryset, self)
            if sort == 'price_asc':
                return queryset.order_by('price')
            elif sort == 'price_desc':
                return queryset.order_by('-price')
            elif sort == 'rating':
                return queryset.annotate(avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))).order_by('-avg_rating', '-created_at')
            elif sort == 'newest':
                return queryset.order_by('-created_at')
            elif sort == 'bestseller':
                return queryset.annotate(total_sold=Sum('orderitem__quantity')).order_by('-total_sold', '-created_at')
        return super().filter_queryset(queryset)

        return qs

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductWriteSerializer
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        products = self.get_queryset().filter(is_featured=True)[:8]
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        products = self.get_queryset().order_by('-created_at')[:8]
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def best_sellers(self, request):
        # Annotate by sold quantity in completed or confirmed orders
        products = self.get_queryset().annotate(
            sales_count=Sum('orderitem__quantity')
        ).order_by('-sales_count', '-created_at')[:8]
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        products = self.get_queryset().filter(is_featured=True).order_by('-stock', '-created_at')[:8]
        if not products.exists():
            products = self.get_queryset().order_by('-created_at')[:8]
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recommended(self, request):
        products = self.get_queryset().order_by('-price')[:8]
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def related(self, request, slug=None):
        product = self.get_object()
        related = self.get_queryset().filter(
            category=product.category
        ).exclude(id=product.id)[:4]
        serializer = ProductListSerializer(related, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def brands(self, request):
        brands = (
            self.get_queryset()
            .exclude(brand='')
            .values_list('brand', flat=True)
            .distinct()
            .order_by('brand')
        )
        return Response(list(brands))
