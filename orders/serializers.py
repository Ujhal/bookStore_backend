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
    class Meta:
        model = Address
        fields = [
            'id', 'address_line_1', 'address_line_2', 'landmark',
            'city', 'state', 'pincode', 'phone_number'
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
            'tracking_number', 'remarks', 'order_items'
        ]
        read_only_fields = [
            'id', 'user', 'transaction_id', 'total_amount',
            'order_date', 'created_at', 'updated_at'
        ]

               
class OrderSerializerSpecific(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'shipping_address',
            'transaction_id',
            'total_amount',
            'status',
            'order_date',
            'created_at',
            'updated_at',
            'order_items','remarks'
        ]
        
class SubOrderItemSerializer(serializers.ModelSerializer):
    book = BookMiniSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'book', 'quantity', 'total_price']

class SubOrderSerializer(serializers.ModelSerializer):
    publisher = UserMiniSerializer(read_only=True)
    items = serializers.SerializerMethodField()

    class Meta:
        model = SubOrder
        fields = [
            'id', 'order', 'publisher', 'status',
            'tracking_number', 'remarks', 'created_at',
            'items'
        ]

    def get_items(self, obj):
        queryset = OrderItem.objects.filter(order=obj.order, assigned_to=obj.publisher)
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

    