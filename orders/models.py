from django.db import models
from django.utils import timezone
from django.db.models import F
import accounts.models as accounts_model
from books.models import Book


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'), 
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(accounts_model.User, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, null=True)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    tracking_number = models.CharField(max_length=50, null=True, blank=True)  # <-- NEW
    remarks = models.TextField(null=True, blank=True)  # <-- NEW
    order_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    def update_total_amount(self):
        total = sum(item.total_price for item in self.order_items.all())
        self.total_amount = total
        self.save(update_fields=['total_amount'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.book.title} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.price_per_unit * self.quantity
        if self._state.adding:
            if self.book.stock_quantity < self.quantity:
                raise ValueError(f"Not enough stock for {self.book.title}")
            self.book.stock_quantity = F('stock_quantity') - self.quantity
            self.book.save(update_fields=["stock_quantity"])
        super().save(*args, **kwargs)
