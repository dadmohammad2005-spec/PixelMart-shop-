import csv
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import OrderListSerializer
from apps.products.models import Product
from apps.products.serializers import ProductListSerializer

User = get_user_model()


class DashboardMetricsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total_orders = Order.objects.count()
        total_customers = User.objects.filter(is_staff=False).count()
        total_active_products = Product.objects.filter(is_active=True).count()
        low_stock_products_count = Product.objects.filter(is_active=True, stock__lte=5).count()
        pending_orders_count = Order.objects.filter(status=Order.STATUS_PENDING).count()

        # Revenue rule: Calculate strictly from confirmed/processing/shipped/delivered orders
        revenue_data = Order.objects.filter(
            status__in=[
                Order.STATUS_CONFIRMED,
                Order.STATUS_PROCESSING,
                Order.STATUS_SHIPPED,
                Order.STATUS_DELIVERED
            ]
        ).aggregate(total=Sum('total_amount'))
        total_revenue = revenue_data['total'] or Decimal('0.00')

        recent_orders = Order.objects.all().order_by('-created_at')[:6]
        low_stock_items = Product.objects.filter(is_active=True, stock__lte=5).order_by('stock')[:6]

        status_breakdown = Order.objects.values('status').annotate(count=Count('id')).order_by('status')

        return Response({
            'metrics': {
                'total_orders': total_orders,
                'total_customers': total_customers,
                'total_active_products': total_active_products,
                'low_stock_products': low_stock_products_count,
                'pending_orders': pending_orders_count,
                'total_revenue': float(total_revenue),
            },
            'recent_orders': OrderListSerializer(recent_orders, many=True).data,
            'low_stock_items': ProductListSerializer(low_stock_items, many=True).data,
            'status_breakdown': list(status_breakdown)
        })


class ExportOrdersCSVView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="shall_shop_orders_report.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Order Number', 'Date', 'Customer Name', 'Customer Email',
            'Status', 'Payment Method', 'Payment Status', 'Subtotal',
            'Shipping', 'Discount', 'Total Amount'
        ])

        orders = Order.objects.all().order_by('-created_at')
        for o in orders:
            writer.writerow([
                o.order_number,
                o.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                o.customer_name,
                o.customer_email,
                o.status,
                o.payment_method,
                o.payment_status,
                str(o.subtotal),
                str(o.shipping_cost),
                str(o.discount_amount),
                str(o.total_amount)
            ])

        return response
