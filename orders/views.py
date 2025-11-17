from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer,OrderSerializerSpecific
from books.models import Book
from accounts.models import Address  
from rest_framework.views import APIView
from .models import Order
from .permissions import IsAdminUserOrSuperuser
# 📦 Retrieve or Update a Specific Order
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUserOrSuperuser  # Assuming this custom permission is defined


# 📦 List and Create Orders
class OrderAPIView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        user = request.user
        book_id = request.data.get('book_id')
        quantity = int(request.data.get('quantity', 1))
        address_id = request.data.get('address_id')

        # validate book & address
        try:
            book = Book.objects.get(id=book_id)
            address = Address.objects.get(id=address_id, user=user)
        except (Book.DoesNotExist, Address.DoesNotExist):
            return Response({'error': 'Invalid book or address'}, status=400)

        # create order
        transaction_id = get_random_string(length=12)

        order = Order.objects.create(
            user=user,
            shipping_address=address,
            total_amount=book.price * quantity,
            status='Pending',
            transaction_id=transaction_id

        )


        # create order item
        # create order item
        OrderItem.objects.create(
            order=order,
            book=book,
            quantity=quantity,
            price_per_unit=book.price
        )


        serializer = self.get_serializer(order)
        return Response(serializer.data, status=201)





class OrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = OrderSerializerSpecific
    permission_classes = [IsAdminUserOrSuperuser]
    queryset = Order.objects.all()

    def get_queryset(self):
        # If the user is an admin, return all orders; otherwise, return only the orders for the authenticated user
        if self.request.user.is_staff:  # check if user is admin
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def get_object(self):
        # Retrieve the order instance, based on `id`
        order_id = self.kwargs.get('pk')
        try:
            order = Order.objects.get(id=order_id)
            return order
            
        except Order.DoesNotExist:
            raise Http404("Order not found.")



# 🧾 Manage Order Items (Add Item to Order)
class OrderItemAPIView(generics.CreateAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, pk=order_id, user=self.request.user)
        book_id = self.request.data.get('book')
        quantity = int(self.request.data.get('quantity', 1))
        book = get_object_or_404(Book, pk=book_id)

        if book.stock_quantity < quantity:
            raise ValueError(f"Not enough stock for {book.title}")

        price_per_unit = book.price or 0
        serializer.save(order=order, book=book, quantity=quantity, price_per_unit=price_per_unit)
        order.update_total_amount()


# ❌ Cancel an Order
class OrderCancelAPIView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Order.objects.all()

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        if order.status in ['Pending', 'Confirmed']:
            order.status = 'Cancelled'
            order.save(update_fields=['status'])
            return Response({'status': 'Order cancelled successfully'})
        return Response({'error': 'Order cannot be cancelled now'}, status=status.HTTP_400_BAD_REQUEST)


class AdminOrderStatusUpdateAPIView(APIView):
    permission_classes = [IsAdminUserOrSuperuser]

    def patch(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        new_status = request.data.get('status')
        tracking_number = request.data.get('tracking_number')
        remarks = request.data.get('remarks')  # <-- NEW

        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]

        if new_status not in valid_statuses:
            return Response({'error': 'Invalid status'}, status=400)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

        # Require tracking number when shipping
        if new_status == 'Shipped' and not tracking_number:
            return Response(
                {'error': 'Tracking number is required when marking order as Shipped'},
                status=400
            )

        order.status = new_status
        if new_status == 'Shipped':
            order.tracking_number = tracking_number

        if remarks:
            order.remarks = remarks  # save remarks

        order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=200)

    
class AdminOrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUserOrSuperuser]

    def get_queryset(self):
        return Order.objects.all().order_by('-created_at')

class AdminOrderByStatusAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUserOrSuperuser]

    def get_queryset(self):
        status = self.request.query_params.get('status')
        queryset = Order.objects.all().order_by('-created_at')
        if status:
            queryset = queryset.filter(status=status)
        return queryset  