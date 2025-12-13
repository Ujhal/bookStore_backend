from django.urls import path
from .views import OrderAPIView, CheckoutRegisterAPIView,OrderDetailAPIView, OrderItemAPIView, OrderCancelAPIView, AdminOrderStatusUpdateAPIView,  AdminForwardOrderAPIView,PublisherSubOrderListAPIView,PublisherSubOrderUpdateAPIView,AdminOrderListAPIView,AdminOrderByStatusAPIView,PublisherSubOrderByStatusAPIView,SubOrderDetailAPIView

urlpatterns = [
    # Orders
    path('orders/', OrderAPIView.as_view(), name='order-list-create'),
    
    path('checkout-register/', CheckoutRegisterAPIView.as_view()),


    # Order Items
    path('orders/<int:order_id>/items/', OrderItemAPIView.as_view(), name='order-items'),

    # Cancel Order
    path('orders/<int:pk>/cancel/', OrderCancelAPIView.as_view(), name='order-cancel'),

    # Admin: Update Order Status
    path('admin/order-update/<int:pk>/', AdminOrderStatusUpdateAPIView.as_view(), name='admin-order-status-update'),
    path('admin/orders/', AdminOrderListAPIView.as_view(), name='admin-order-list'),
    path('admin/orders/<int:pk>/', OrderDetailAPIView.as_view(), name='order-retrieve-update'),
    path('admin/orders-by-status/', AdminOrderByStatusAPIView.as_view(), name='admin-orders-by-status'),

    path('admin/order/<int:pk>/forward/', AdminForwardOrderAPIView.as_view()),

    # Publisher Routes
    path('publisher/suborders/', PublisherSubOrderListAPIView.as_view()),
    path('publisher/suborder/<int:pk>/update/', PublisherSubOrderUpdateAPIView.as_view()),
    
    path("publisher/suborders/status/",PublisherSubOrderByStatusAPIView.as_view(),name="publisher-suborders-by-status"),
    path("publisher/suborders/<int:id>/",SubOrderDetailAPIView.as_view(),name="publisher-suborder-detail"
),

]
