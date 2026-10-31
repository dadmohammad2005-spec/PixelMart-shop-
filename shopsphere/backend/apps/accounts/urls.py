from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    ChangePasswordView,
    AddressViewSet,
    CustomerAdminViewSet,
    auth_status,
)

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')
router.register(r'admin/customers', CustomerAdminViewSet, basename='admin-customer')

urlpatterns = [
    path('status/', auth_status, name='auth-status'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('', include(router.urls)),
]
