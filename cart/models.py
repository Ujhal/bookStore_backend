from django.db import models
from django.conf import settings
from books.models import Book

class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='carts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Cart {self.id} for {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, 
        related_name='items', 
        on_delete=models.CASCADE
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.book.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.book.title}"
