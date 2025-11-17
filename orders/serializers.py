from rest_framework import serializers
from .models import Order, OrderItem
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
            'id', 'user', 'shipping_address', 'transaction_id',
            'total_amount', 'status', 'order_date',
            'created_at', 'updated_at', 'order_items',
            'tracking_number','remarks'  # <-- ADD THIS
        ]
        read_only_fields = ['user', 'total_amount', 'created_at', 'updated_at', 'order_date']

               
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
