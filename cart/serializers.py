from rest_framework import serializers
from .models import Cart, CartItem
from books.serializers import BookSerializer
from books.models import Book

class CartItemSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        source='book', queryset=Book.objects.all(), write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'book', 'book_id', 'quantity', 'subtotal']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price']

    def get_total_price(self, obj):
        return obj.total_price()
