from django.contrib import admin
from .models import Coupon, CouponUsage, Announcement, NewsletterSubscriber


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_order_amount', 'used_count', 'usage_limit', 'is_active', 'end_date')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code',)


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'user', 'order', 'used_at')
    search_fields = ('coupon__code', 'user__email', 'order__order_number')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('message', 'link_url', 'is_active', 'updated_at')
    list_editable = ('is_active',)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'subscribed_at')
    list_filter = ('is_active',)
    search_fields = ('email',)
