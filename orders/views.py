# Django & Utilities
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from .pagination import OrderPagination
from decimal import Decimal

 # Sort by ID descending

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
from django.contrib.auth import get_user_model
from django.db import transaction



from books.models import Book

from .models import Order, OrderItem,SubOrder
from .serializers import OrderSerializer, OrderItemSerializer, OrderSerializerSpecific,SubOrderSerializer,UserOrderDetailSerializer,SubOrderDetailSerializer,OrderSummarySerializer
from .permissions import IsAdminUserOrSuperuser,IsPublisher,IsPublisherOrAdmin

class OrderAPIView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        address_id = request.data.get('address_id')
        items = request.data.get('items', None)

        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            return Response({'error': 'Invalid address'}, status=400)

        # 🚚 Delivery charge logic
        delivery_charge = Decimal("0.00")
        if address.state.code != "SK":  # Not Sikkim
            delivery_charge = Decimal("100.00")

        order = Order.objects.create(
            user=user,
            shipping_address=address,
            status='Pending',
            delivery_charge=delivery_charge
        )

        from collections import defaultdict
        items_by_stakeholder = defaultdict(list)

        if items is not None:
            for item_data in items:
                book_id = item_data.get('book_id')
                quantity = int(item_data.get('quantity', 1))

                try:
                    book = Book.objects.get(id=book_id)
                except Book.DoesNotExist:
                    order.delete()
                    return Response(
                        {'error': f'Invalid book ID: {book_id}'},
                        status=400
                    )

                order_item = OrderItem.objects.create(
                    order=order,
                    book=book,
                    quantity=quantity,
                    price_per_unit=book.price,
                    total_price=book.price * quantity,
                    assigned_to=book.created_by
                )

                items_by_stakeholder[book.created_by].append(order_item)

        # ✅ Update total including delivery
        order.update_total_amount()

        return Response({
            "order_id": order.id,
            "items_total": order.total_amount - order.delivery_charge,
            "delivery_charge": order.delivery_charge,
            "total_amount": order.total_amount,
            "status": order.status
        }, status=201)


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
        User = get_user_model()

        email = data.get("email")
        phone = data.get("phone_number")

        # ---------------------------
        # 1️⃣ Duplicate user check
        # ---------------------------
        if email and User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already registered. Please login."},
                status=400
            )

        if phone and User.objects.filter(phone_number=phone).exists():
            return Response(
                {"error": "Phone number already registered. Please login."},
                status=400
            )

        items = data.get("items", [])
        if not items:
            return Response({"error": "Cart is empty"}, status=400)

        try:
            with transaction.atomic():

                # ---------------------------
                # 2️⃣ Create User
                # ---------------------------
                user_serializer = UserRegistrationSerializer(data={
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "email": email,
                    "phone_number": phone,
                    "password": data["password"],
                    "role": 2
                })
                user_serializer.is_valid(raise_exception=True)
                user = user_serializer.save()

                # ---------------------------
                # 3️⃣ Create Address
                # ---------------------------
                address = Address.objects.create(
                    user=user,
                    address_line_1=data["address_line_1"],
                    address_line_2=data.get("address_line_2", ""),
                    landmark=data.get("landmark", ""),
                    city=data["city"],
                    state_id=data["state"],
                    pincode=data["pincode"],
                    phone_number=phone
                )

                # ---------------------------
                # 4️⃣ Delivery Charge Logic
                # ---------------------------
                delivery_charge = Decimal("0.00")
                if address.state.code != "SK":
                    delivery_charge = Decimal("100.00")

                # ---------------------------
                # 5️⃣ Create Order
                # ---------------------------
                order = Order.objects.create(
                    user=user,
                    shipping_address=address,
                    status="Pending",
                    delivery_charge=delivery_charge,
                    transaction_id=get_random_string(12)
                )

                # ---------------------------
                # 6️⃣ Create Order Items
                # ---------------------------
                for item in items:
                    book = Book.objects.get(id=item["book_id"])
                    quantity = int(item.get("quantity", 1))

                    OrderItem.objects.create(
                        order=order,
                        book=book,
                        quantity=quantity,
                        price_per_unit=book.price,
                        total_price=book.price * quantity,
                        assigned_to=book.created_by
                    )

                # ---------------------------
                # 7️⃣ Update Order Total
                # ---------------------------
                order.update_total_amount()

                # ---------------------------
                # 8️⃣ Generate JWT Tokens
                # ---------------------------
                refresh = RefreshToken.for_user(user)

                return Response({
                    "message": "User registered & order placed successfully",
                    "order_id": order.id,
                    "total_amount": order.total_amount,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                }, status=201)

        except Book.DoesNotExist:
            return Response({"error": "Invalid book in cart"}, status=400)

        except Exception as e:
            return Response(
                {"error": "Checkout failed", "details": str(e)},
                status=500
            )

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
    pagination_class = OrderPagination  # <-- Add this
    def get_queryset(self):
        return Order.objects.exclude(status='Pending').order_by('id')


class AdminOrderByStatusAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUserOrSuperuser]
    pagination_class = OrderPagination
    
    def get_queryset(self):
        status = self.request.query_params.get('status')
        queryset = Order.objects.all().order_by('-created_at')
        if status:
            queryset = queryset.filter(status=status)
        return queryset  



class PublisherSubOrderUpdateAPIView(APIView):
    permission_classes = [IsPublisherOrAdmin]

    def patch(self, request, pk):
        try:
            # Allow admin OR publisher
            if request.user.is_staff:
                suborder = SubOrder.objects.get(id=pk)
            else:
                suborder = SubOrder.objects.get(id=pk, publisher=request.user)

        except SubOrder.DoesNotExist:
            return Response(
                {'error': 'SubOrder not found or not assigned to you'},
                status=404
            )

        status_value = request.data.get('status')
        tracking = request.data.get('tracking_number')
        remarks = request.data.get('remarks')

        # Validate status
        if status_value and status_value not in dict(Order.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=400)

        # If status is Shipped, tracking number is required
        if status_value == 'Shipped' and not tracking:
            return Response({'error': 'Tracking number required'}, status=400)

        with transaction.atomic():
            # Update fields
            if status_value:
                suborder.status = status_value
            if tracking:
                suborder.tracking_number = tracking
            if remarks is not None:
                suborder.remarks = remarks

            suborder.save()

            # 🔥 MAIN LOGIC STARTS HERE
            order = suborder.order
            suborders = order.sub_orders.all()

            statuses = list(suborders.values_list('status', flat=True))

            # Check if all statuses are the same
            if len(set(statuses)) == 1:
                new_status = statuses[0]

                # Avoid unnecessary save
                if order.status != new_status:
                    order.status = new_status
                    order.save(update_fields=['status'])

        return Response(SubOrderSerializer(suborder).data)
class PublisherSubOrderListAPIView(generics.ListAPIView):
    serializer_class = SubOrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OrderPagination

    def get_queryset(self):
        user = self.request.user

        # Only allow users with role '1' or '3'
        if user.role not in [1, 3]:
            return SubOrder.objects.none()

        # Get all SubOrders for the publisher, excluding "Pending" status
        queryset = (
            SubOrder.objects
            .filter(publisher=user)
            .exclude(status__iexact='Pending')  # Exclude Pending
            .select_related("order", "publisher")
            .prefetch_related("order__order_items")
            .order_by("-created_at")
        )

        return queryset
        

class PublisherSubOrderByStatusAPIView(generics.ListAPIView):
    serializer_class = SubOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print(type(user.role), user.role)

        # ✅ FIXED ROLE CHECK (STRING)
        if user.role not in [3, 1]:
            return SubOrder.objects.none()

        queryset = (
            SubOrder.objects
            .filter(publisher=user)
            .select_related("order", "publisher")
            .prefetch_related("order__order_items")
            .order_by("-created_at")
        )

        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status__iexact=status)

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
        

#orderlistforcustomers 
class OrderCustomerAPIView(generics.ListCreateAPIView):
    serializer_class = OrderSummarySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OrderPagination

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

#orderlistforAdmin
class OrderAdminAPIView(generics.ListCreateAPIView):
    serializer_class = OrderSummarySerializer
    permission_classes = [IsAdminUserOrSuperuser]
    pagination_class = OrderPagination

    def get_queryset(self):
        return Order.objects.all().order_by('-created_at')
       

class UserOrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = UserOrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_object(self):
        try:
            return self.get_queryset().get(pk=self.kwargs['pk'])
        except Order.DoesNotExist:
            raise Http404("Order not found")