from django.db.models import F
from books.models import Book

def reduce_book_stock(order):
    for item in order.order_items.all():
        Book.objects.filter(id=item.book.id).update(
            stock_quantity=F("stock_quantity") - item.quantity
        )