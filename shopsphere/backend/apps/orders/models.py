import uuid
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Order(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_PROCESSING = 'PROCESSING'
    STATUS_SHIPPED = 'SHIPPED'
    STATUS_DELIVERED = 'DELIVERED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    PAYMENT_METHOD_COD = 'COD'
    PAYMENT_METHOD_STRIPE = 'STRIPE'
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_COD, 'Cash on Delivery'),
        (PAYMENT_METHOD_STRIPE, 'Stripe (Credit / Debit Card)'),
    ]

    PAYMENT_STATUS_PENDING = 'PENDING'
    PAYMENT_STATUS_PAID = 'PAID'
    PAYMENT_STATUS_FAILED = 'FAILED'
    PAYMENT_STATUS_REFUNDED = 'REFUNDED'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_PAID, 'Paid'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
        (PAYMENT_STATUS_REFUNDED, 'Refunded'),
    ]

    order_number = models.CharField(max_length=40, unique=True, editable=False, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='orders'
    )

    # Customer Contact
    customer_email = models.EmailField(db_index=True)
    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=30)

    # Shipping Address Snapshot
    shipping_name = models.CharField(max_length=150)
    shipping_phone = models.CharField(max_length=30)
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_address_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default='United States')

    # Logistics & Financials
    shipping_method = models.CharField(max_length=50, default='standard')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, validators=[MinValueValidator(0.0)])
    coupon_code = models.CharField(max_length=32, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_METHOD_COD)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING, db_index=True)

    order_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            date_str = timezone.now().strftime('%Y%m%d')
            rand_suffix = uuid.uuid4().hex[:6].upper()
            self.order_number = f"ORD-{date_str}-{rand_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} - {self.customer_name} (${self.total_amount})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def is_paid(self):
        return self.payment_status == self.PAYMENT_STATUS_PAID

    @property
    def can_cancel(self):
        return self.status in [self.STATUS_PENDING, self.STATUS_CONFIRMED]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', null=True, on_delete=models.SET_NULL)

    # Immutable historical snapshots
    product_name = models.CharField(max_length=255)
    product_sku = models.CharField(max_length=64)
    product_image_url = models.CharField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    line_total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.0)])

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.quantity} x {self.product_name} in {self.order.order_number}"
