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

    user = models.ForeignKey(accounts_model.User, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey('accounts.Address', on_delete=models.SET_NULL, null=True)
    transaction_id = models.CharField(max_length=100, unique=True,blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    order_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    invoice_pdf = models.FileField(upload_to="invoices/orders/", blank=True, null=True)

    payment_status = models.CharField(
        max_length=20,
        choices=(
            ('Pending', 'Pending'),
            ('Paid', 'Paid'),
            ('Failed', 'Failed'),
        ),
        default='Pending'
    )
    delivery_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    razorpay_order_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    def update_total_amount(self):
        total = sum(item.total_price for item in self.order_items.all())
        self.total_amount = total + self.delivery_charge
        self.save(update_fields=['total_amount'])

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    assigned_to = models.ForeignKey(
        accounts_model.User,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_order_items'
    )

    

    def __str__(self):
        return f"{self.book.title} x{self.quantity}"


class SubOrder(models.Model):  
    order = models.ForeignKey(Order, related_name='sub_orders', on_delete=models.CASCADE)
    publisher = models.ForeignKey(accounts_model.User, on_delete=models.CASCADE, blank=True, null=True)

    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES, default='Pending')
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    
    invoice_pdf = models.FileField(upload_to="invoices/suborders/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SubOrder #{self.id} for {self.publisher.username}"

