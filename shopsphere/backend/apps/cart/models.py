from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    coupon_code = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.email}"
        return f"Anonymous Cart ({self.session_key})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        total = sum(item.line_total for item in self.items.all())
        return Decimal(str(total)).quantize(Decimal('0.01'))

    @property
    def is_empty(self):
        return self.items.count() == 0

    def calculate_totals(self, shipping_rule='standard'):
        """
        Secure backend calculation of subtotal, discount, shipping, and grand total.
        """
        subtotal = self.subtotal
        discount_amount = Decimal('0.00')

        # Check coupon if applied
        if self.coupon_code:
            try:
                from apps.promotions.models import Coupon
                coupon = Coupon.objects.filter(code__iexact=self.coupon_code, is_active=True).first()
                if coupon and coupon.is_valid():
                    discount_amount = coupon.calculate_discount(subtotal)
            except Exception:
                discount_amount = Decimal('0.00')

        # Shipping rules: Free shipping over $100, otherwise Standard $9.99 or Express $19.99
        if subtotal == 0:
            shipping_cost = Decimal('0.00')
        elif shipping_rule == 'express':
            shipping_cost = Decimal('19.99')
        elif subtotal >= Decimal('100.00'):
            shipping_cost = Decimal('0.00')
        else:
            shipping_cost = Decimal('9.99')

        grand_total = max(Decimal('0.00'), subtotal - discount_amount + shipping_cost)

        return {
            'subtotal': subtotal,
            'discount_amount': discount_amount,
            'shipping_cost': shipping_cost,
            'grand_total': grand_total.quantize(Decimal('0.01')),
            'free_shipping_threshold': Decimal('100.00'),
            'amount_to_free_shipping': max(Decimal('0.00'), Decimal('100.00') - subtotal)
        }


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'product')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def unit_price(self):
        return self.product.current_price

    @property
    def line_total(self):
        return (self.unit_price * self.quantity).quantize(Decimal('0.01'))

    @property
    def in_stock(self):
        return self.product.stock >= self.quantity

    @property
    def available_stock(self):
        return self.product.stock
