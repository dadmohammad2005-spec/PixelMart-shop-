from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    DISCOUNT_PERCENTAGE = 'PERCENTAGE'
    DISCOUNT_FIXED = 'FIXED'
    DISCOUNT_TYPE_CHOICES = [
        (DISCOUNT_PERCENTAGE, 'Percentage (%)'),
        (DISCOUNT_FIXED, 'Fixed Amount ($)'),
    ]

    code = models.CharField(max_length=32, unique=True, db_index=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default=DISCOUNT_PERCENTAGE)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Total maximum uses for this coupon (leave blank for unlimited)")
    used_count = models.PositiveIntegerField(default=0)
    per_user_limit = models.PositiveIntegerField(default=1, help_text="Max uses per customer")
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        desc = f"{self.discount_value}%" if self.discount_type == self.DISCOUNT_PERCENTAGE else f"${self.discount_value}"
        return f"{self.code} ({desc} off)"

    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False
        return True

    def validate_for_order(self, subtotal, user=None):
        if not self.is_valid():
            return False, "This coupon has expired or is no longer active."

        if subtotal < self.min_order_amount:
            return False, f"Minimum order amount of ${self.min_order_amount:.2f} is required for this coupon."

        if user and user.is_authenticated:
            user_usages = self.usages.filter(user=user).count()
            if user_usages >= self.per_user_limit:
                return False, f"You have already reached the limit of {self.per_user_limit} use(s) for this coupon."

        return True, "Coupon is valid."

    def calculate_discount(self, subtotal):
        if subtotal <= 0:
            return Decimal('0.00')

        if self.discount_type == self.DISCOUNT_PERCENTAGE:
            discount = (subtotal * self.discount_value) / Decimal('100.00')
            if self.max_discount_amount is not None:
                discount = min(discount, self.max_discount_amount)
        else:
            discount = self.discount_value

        # Cannot exceed subtotal
        return min(discount, subtotal).quantize(Decimal('0.01'))


class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coupon_usages')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='coupon_usages')
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Coupon Usage'
        verbose_name_plural = 'Coupon Usages'


class Announcement(models.Model):
    message = models.CharField(max_length=255)
    link_url = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Announcement Bar'
        verbose_name_plural = 'Announcement Bars'

    def __str__(self):
        return self.message[:50]


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Newsletter Subscriber'
        verbose_name_plural = 'Newsletter Subscribers'
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email
