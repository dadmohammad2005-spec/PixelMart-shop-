from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    fieldsets = UserAdmin.fieldsets + (
        ('ShopSphere Additional Info', {'fields': ('phone_number', 'avatar')}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'state', 'country', 'is_default_shipping', 'is_default_billing')
    list_filter = ('is_default_shipping', 'is_default_billing', 'country')
    search_fields = ('user__email', 'full_name', 'address_line1', 'city', 'postal_code')
