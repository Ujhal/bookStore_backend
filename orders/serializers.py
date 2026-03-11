from rest_framework import serializers
from .models import Order, OrderItem,SubOrder
from books.models import Book
from accounts.models import Address 
from accounts.models import User

 
class BookMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'price', 'author', 'publisher', 'language']

class AddressSerializer(serializers.ModelSerializer):
    state_name = serializers.ReadOnlyField(source='state.name')

    class Meta:
        model = Address
        fields = [
            'id', 'address_line_1', 'address_line_2', 'landmark',
            'city', 'state', 'pincode', 'phone_number','state_name'
        ]
class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone_number']

class OrderItemSerializer(serializers.ModelSerializer):
    book = BookMiniSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'book', 'quantity', 'price_per_unit', 'total_price']
        
class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'shipping_address', 'transaction_id', 'total_amount',
            'status', 'order_date', 'created_at', 'updated_at',
            'tracking_number', 'remarks', 'order_items','delivery_charge'
        ]
        read_only_fields = [
            'id', 'user', 'transaction_id', 'total_amount',
            'order_date', 'created_at', 'updated_at'
        ]

class OrderSerializerSpecific(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    sub_orders = serializers.SerializerMethodField()  # Custom representation

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'shipping_address',
            'transaction_id',
            'total_amount',
            'delivery_charge',
            'status',
            'order_date',
            'created_at',
            'updated_at',
            'sub_orders',
            'remarks',
            'invoice_pdf'
        ]

    def get_sub_orders(self, obj):
        """
        Custom representation of sub-orders to include:
        - publisher info
        - status, tracking_number, remarks
        - items assigned to that publisher
        Avoid duplicating main order_items
        """
        suborders_list = []
        for sub in obj.sub_orders.all():
            # Only include minimal item info
            items = sub.order.order_items.filter(assigned_to=sub.publisher).values(
                'id',
                'book__title',
                'quantity',
                'total_price'
            )
            suborders_list.append({
                'id': sub.id,
                'publisher': {
                    'id': sub.publisher.id,
                    'username': sub.publisher.username,
                    'email': sub.publisher.email,
                    'role': sub.publisher.role,
                    'phone_number': sub.publisher.phone_number
                },
                'status': sub.status,
                'tracking_number': sub.tracking_number,
                'remarks': sub.remarks,
                'created_at': sub.created_at,
                'items': list(items)
            })
        return suborders_list


class SubOrderItemSerializer(serializers.ModelSerializer):
    book = BookMiniSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'book', 'quantity', 'total_price']

class SubOrderSerializer(serializers.ModelSerializer):
    publisher = UserMiniSerializer(read_only=True)
    order_id = serializers.IntegerField(source='order.id', read_only=True)
    suborder_id = serializers.IntegerField(source='id', read_only=True)
    transaction_id = serializers.CharField(source='order.transaction_id', read_only=True)

    items = serializers.SerializerMethodField()

    class Meta:
        model = SubOrder
        fields = [
            'suborder_id',
            'order_id',
            'publisher',
            'status',
            'tracking_number',
            'remarks',
            'created_at',
            'items',
            'transaction_id'
        ]

    def get_items(self, obj):
        queryset = OrderItem.objects.filter(
            order=obj.order,
            assigned_to=obj.publisher
        )
        return SubOrderItemSerializer(queryset, many=True).data

class SubOrderDetailSerializer(serializers.ModelSerializer):
    publisher = UserMiniSerializer(read_only=True)
    items = serializers.SerializerMethodField()
    order_details = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()

    class Meta:
        model = SubOrder
        fields = [
            'id',
            'publisher',
            'status',
            'tracking_number',
            'remarks',
            'created_at',
            'items',
            'order_details',
            'shipping_address'
        ]

    def get_items(self, obj):
        # Items assigned to this suborder's publisher
        items = obj.order.order_items.filter(assigned_to=obj.publisher)
        return SubOrderItemSerializer(items, many=True).data

    def get_order_details(self, obj):
        order = obj.order
        return {
            'order_id': order.id,
            'transaction_id': order.transaction_id,
            'order_date': order.order_date,
            'total_amount': order.total_amount,
            'status': order.status
        }

    def get_shipping_address(self, obj):
        address = obj.order.shipping_address
        if address:
            return AddressSerializer(address).data
        return None

class OrderSummarySerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='id')  # Map 'id' to 'order_id'

    class Meta:
        model = Order
        fields = ['order_id', 'order_date', 'status', 'transaction_id']
        read_only_fields = fields   


class UserOrderDetailSerializer(serializers.ModelSerializer):
    sub_orders = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id',
            'transaction_id',
            'total_amount',
            'status',
            'order_date',
            'remarks',
            'sub_orders',
            'invoice_pdf'
        ]

    def get_sub_orders(self, obj):
        suborders_data = []

        for sub in obj.sub_orders.all():
            items = sub.order.order_items.filter(
                assigned_to=sub.publisher
            ).select_related('book').values(
                'id',
                'book__title',
                'quantity'
            )

            suborders_data.append({
                'id': sub.id,
                'status': sub.status,
                'tracking_number': sub.tracking_number,
                'created_at': sub.created_at,
                'items': list(items)
            })

        return suborders_data