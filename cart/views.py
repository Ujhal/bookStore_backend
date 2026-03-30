from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from books.models import Book

class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        book_id = request.data.get('book_id')
        quantity = int(request.data.get('quantity', 1))
        cart, _ = Cart.objects.get_or_create(user=request.user)
        book = Book.objects.get(id=book_id)

        # Add or update item
        item, created = CartItem.objects.get_or_create(cart=cart, book=book)
 
        if created:
            item.quantity = quantity   # set directly
        else:
            item.quantity += quantity  # increment

        item.save()


        return Response({"detail": f"{book.title} added to cart."}, status=status.HTTP_200_OK)
    
    def delete(self, request, book_id=None):
        cart = Cart.objects.get(user=request.user)
        deleted, _ = CartItem.objects.filter(cart=cart, book_id=book_id).delete()
        if deleted:
            return Response({"detail": "Item removed from cart."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Item not found in cart."}, status=status.HTTP_404_NOT_FOUND)

