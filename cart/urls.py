from django.urls import path
from .views import CartView

# cart/urls.py
urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('<int:book_id>/', CartView.as_view(), name='cart-item'),
]

