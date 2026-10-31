from django.contrib.auth import authenticate, login, logout, get_user_model
from django.middleware.csrf import get_token
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Count, Sum, Q
from .models import Address
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    AddressSerializer,
    CustomerAdminSerializer,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.backend = 'apps.accounts.backends.EmailOrUsernameBackend'
            old_session_key = request.session.session_key
            login(request, user, backend='apps.accounts.backends.EmailOrUsernameBackend')
            # Try to merge session cart if available
            try:
                from apps.cart.utils import merge_session_cart
                merge_session_cart(request, user, old_session_key=old_session_key)
            except Exception:
                pass

            profile_data = UserProfileSerializer(user).data
            return Response(
                {
                    "message": "Registration successful.",
                    "user": profile_data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email_or_username = request.data.get('email') or request.data.get('username')
        password = request.data.get('password')

        if not email_or_username or not password:
            return Response(
                {"error": "Please provide both email/username and password."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Allow authentication by either email or username using EmailOrUsernameBackend
        user = authenticate(request, username=email_or_username, password=password)

        if user is not None:
            if not user.is_active:
                return Response(
                    {"error": "This account is inactive. Please contact support."},
                    status=status.HTTP_403_FORBIDDEN
                )
            old_session_key = request.session.session_key
            login(request, user, backend='apps.accounts.backends.EmailOrUsernameBackend')
            # Merge session cart to user cart
            try:
                from apps.cart.utils import merge_session_cart
                merge_session_cart(request, user, old_session_key=old_session_key)
            except Exception:
                pass

            return Response(
                {
                    "message": "Login successful.",
                    "user": UserProfileSerializer(user).data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {"error": "Invalid credentials. Please verify your email/username and password."},
            status=status.HTTP_401_UNAUTHORIZED
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {"old_password": ["Current password is incorrect."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            user.backend = 'apps.accounts.backends.EmailOrUsernameBackend'
            # Keep user logged in after password change
            login(request, user, backend='apps.accounts.backends.EmailOrUsernameBackend')
            return Response({"message": "Password updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class CustomerAdminViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerAdminSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return User.objects.annotate(
            orders_count=Count('orders'),
            total_spent=Sum('orders__total_amount', filter=Q(orders__status__in=['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED']))
        ).order_by('-date_joined')


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def auth_status(request):
    """
    Returns CSRF token and current user session state.
    """
    token = get_token(request)
    is_auth = request.user.is_authenticated
    user_data = UserProfileSerializer(request.user).data if is_auth else None
    return Response({
        "csrf_token": token,
        "is_authenticated": is_auth,
        "user": user_data
    })
