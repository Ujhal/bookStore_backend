from django.urls import path
from .views import OrderAPIView, OrderDetailAPIView, OrderItemAPIView, OrderCancelAPIView, AdminOrderStatusUpdateAPIView,AdminOrderListAPIView,AdminOrderByStatusAPIView

urlpatterns = [
    # Orders
    path('orders/', OrderAPIView.as_view(), name='order-list-create'),
    

    # Order Items
    path('orders/<int:order_id>/items/', OrderItemAPIView.as_view(), name='order-items'),

    # Cancel Order
    path('orders/<int:pk>/cancel/', OrderCancelAPIView.as_view(), name='order-cancel'),

    # Admin: Update Order Status
    path('admin/order-update/<int:pk>/', AdminOrderStatusUpdateAPIView.as_view(), name='admin-order-status-update'),
    path('admin/orders/', AdminOrderListAPIView.as_view(), name='admin-order-list'),
    path('admin/orders/<int:pk>/', OrderDetailAPIView.as_view(), name='order-retrieve-update'),
    path('admin/orders-by-status/', AdminOrderByStatusAPIView.as_view(), name='admin-orders-by-status'),
]
