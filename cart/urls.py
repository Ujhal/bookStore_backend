from django.urls import path
from .views import CartView

# cart/urls.py
urlpatterns = [
    path('', CartView.as_view(), name='cart'),  # GET: view cart, POST: add/update item
    path('remove/<int:book_id>/', CartView.as_view(), name='cart-item-remove'),  # DELETE: remove
]


