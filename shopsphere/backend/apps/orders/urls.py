from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CheckoutView,
    UserOrderListView,
    OrderDetailView,
    OrderCancelView,
    AdminOrderViewSet,
)
from .dashboard_views import DashboardMetricsView, ExportOrdersCSVView

router = DefaultRouter()
router.register(r'admin/manage', AdminOrderViewSet, basename='admin-order-manage')

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='order-checkout'),
    path('my-orders/', UserOrderListView.as_view(), name='user-orders'),
    path('dashboard/metrics/', DashboardMetricsView.as_view(), name='admin-dashboard-metrics'),
    path('dashboard/export-csv/', ExportOrdersCSVView.as_view(), name='admin-dashboard-export'),
    path('<str:order_number>/', OrderDetailView.as_view(), name='order-detail'),
    path('<str:order_number>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
    path('', include(router.urls)),
]
