# Django & Utilities
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string

# DRF Core
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

# JWT
from rest_framework_simplejwt.tokens import RefreshToken

# App Models & Serializers
from accounts.models import User, Address
from accounts.serializers import UserRegistrationSerializer, AddressSerializer

from books.models import Book

from .models import Order, OrderItem,SubOrder
from .serializers import OrderSerializer, OrderItemSerializer, OrderSerializerSpecific,SubOrderSerializer,SubOrderDetailSerializer
from .permissions import IsAdminUserOrSuperuser


class OrderAPIView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print("\n[DEBUG] Fetching orders for user:", self.request.user.username)
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        user = request.user
        print("\n[DEBUG] Order creation requested by:", user.username)

        address_id = request.data.get('address_id')
        items = request.data.get('items', None)

        # Validate address
        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            return Response({'error': 'Invalid address'}, status=400)

        transaction_id = get_random_string(12)
        order = Order.objects.create(
            user=user,
            shipping_address=address,
            transaction_id=transaction_id,
            status='Pending'
        )

        from collections import defaultdict
        items_by_stakeholder = defaultdict(list)

        # CASE 1: multi-item payload
        if items is not None:
            for item_data in items:
                book_id = item_data.get('book_id')
                quantity = int(item_data.get('quantity', 1))
                try:
                    book = Book.objects.get(id=book_id)
                except Book.DoesNotExist:
                    order.delete()
                    return Response({'error': f'Invalid book ID: {book_id}'}, status=400)

                order_item = OrderItem.objects.create(
                    order=order,
                    book=book,
                    quantity=quantity,
                    price_per_unit=book.price,
                    total_price=book.price * quantity,
                    assigned_to=book.created_by
                )
                items_by_stakeholder[book.created_by].append(order_item)

        # CASE 2: single-item payload
        else:
            book_id = request.data.get('book_id')
            quantity = int(request.data.get('quantity', 1))
            try:
                book = Book.objects.get(id=book_id)
            except Book.DoesNotExist:
                order.delete()
                return Response({'error': f'Invalid book ID: {book_id}'}, status=400)

            order_item = OrderItem.objects.create(
                order=order,
                book=book,
                quantity=quantity,
                price_per_unit=book.price,
                total_price=book.price * quantity,
                assigned_to=book.created_by
            )
            items_by_stakeholder[book.created_by].append(order_item)

        # Update total and create suborders
        order.update_total_amount()
        for stakeholder, stakeholder_items in items_by_stakeholder.items():
            if stakeholder:
                SubOrder.objects.create(
                    order=order,
                    publisher=stakeholder,
                    status='Pending'
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





class CheckoutRegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        data = request.data
        
        # ---------------------------
        # 1. Register the user
        # ---------------------------
        user_serializer = UserRegistrationSerializer(data={
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "email": data["email"],
            "phone_number": data["phone_number"],
            "password": data["password"],
            "username": data["email"],     # optional but recommended
            "role": 2
        })

        if not user_serializer.is_valid():
            return Response(user_serializer.errors, status=400)

        user = user_serializer.save()

        # ---------------------------
        # 2. Create Address
        # ---------------------------
        address = Address.objects.create(
            user=user,
            address_line_1=data["address_line_1"],
            address_line_2=data.get("address_line_2", ""),
            landmark=data.get("landmark", ""),
            city=data["city"],
            state=data["state"],
            pincode=data["pincode"],
            phone_number=data["phone_number"]
        )

        # ---------------------------
        # 3. Create Order
        # ---------------------------
        try:
            book = Book.objects.get(id=data["book_id"])
        except Book.DoesNotExist:
            return Response({"error": "Invalid book"}, status=400)

        transaction_id = get_random_string(12)

        order = Order.objects.create(
            user=user,
            shipping_address=address,
            transaction_id=transaction_id,
            total_amount=book.price * int(data["quantity"]),
            status="Pending"
        )

        # ---------------------------
        # 4. Create Order Item
        # ---------------------------
        OrderItem.objects.create(
            order=order,
            book=book,
            quantity=data["quantity"],
            price_per_unit=book.price
        )

        # ---------------------------
        # 5. Generate JWT Token
        # ---------------------------
        refresh = RefreshToken.for_user(user)

        # ---------------------------
        # 6. Response
        # ---------------------------
        return Response({
            "message": "User registered & order placed!",
            "order_id": order.id,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }, status=201)

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
    permission_classes = [IsAdminUserOrSuperuser]
    serializer_class = OrderSerializer

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

class AdminForwardOrderAPIView(APIView):
    permission_classes = [IsAdminUserOrSuperuser]

    def post(self, request, pk):
        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

        publisher_map = {}  # publisher_id -> list of items

        for item in order.order_items.all():
            publisher = item.book.created_by  # book owner

            item.assigned_to = publisher
            item.forwarded = True
            item.save()

            if publisher.id not in publisher_map:
                publisher_map[publisher.id] = []
            publisher_map[publisher.id].append(item)

        # Create SubOrders
        for publisher_id, items in publisher_map.items():
            SubOrder.objects.create(order=order, publisher_id=publisher_id)

        return Response({'message': 'Order forwarded to publishers'}, status=200)


class PublisherSubOrderUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            suborder = SubOrder.objects.get(id=pk, publisher=request.user)
        except SubOrder.DoesNotExist:
            return Response({'error': 'SubOrder not found'}, status=404)

        status = request.data.get('status')
        tracking = request.data.get('tracking_number')
        remarks = request.data.get('remarks')

        if status not in dict(Order.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=400)

        # Validation
        if status == 'Shipped' and not tracking:
            return Response({'error': 'Tracking number required'}, status=400)

        suborder.status = status
        if tracking:
            suborder.tracking_number = tracking
        if remarks:
            suborder.remarks = remarks

        suborder.save()
        return Response(SubOrderSerializer(suborder).data)



class PublisherSubOrderListAPIView(generics.ListAPIView):
    serializer_class = SubOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Only publishers or admins should access this
        if user.role not in ['publisher', 'admin']:
            return SubOrder.objects.none()

        # Return all suborders belonging to logged-in publisher/admin
        return SubOrder.objects.filter(
            publisher=user
        ).select_related(
            "order", "publisher"
        ).order_by("-created_at")
        

class PublisherSubOrderByStatusAPIView(generics.ListAPIView):
    serializer_class = SubOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Only publishers or admins allowed
        if user.role not in [1,3]:
            return SubOrder.objects.none()

        # Get optional ?status= query param
        status = self.request.query_params.get('status', None)

        queryset = SubOrder.objects.filter(
            publisher=user   # restrict to logged-in publisher ONLY
        ).select_related(
            "order", "publisher"
        ).prefetch_related(
            "order__order_items"
        ).order_by("-created_at")

        # If status filter applied
        if status:
            queryset = queryset.filter(status=status)

        return queryset
        
class SubOrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = SubOrderDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    queryset = SubOrder.objects.all()

    def get_queryset(self):
        user = self.request.user

        # Only allow access if publisher/admin owns this suborder
        if user.role in [1, 3]:  # Admin=1, Publisher=3
            return SubOrder.objects.filter(publisher=user)
        return SubOrder.objects.none()
        