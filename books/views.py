from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.db.models import Count
from .permissions import IsPublisher,IsAdmin


from .models import Author, Category, SubCategory, Book, Review
from .serializers import (
    AuthorSerializer,
    CategorySerializer,
    SubCategorySerializer,
    BookSerializer,
    ReviewSerializer
)


# Utility: Check user role



# =====================================================================================
#                                   AUTHOR API
# =====================================================================================

class AuthorAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        author_id = kwargs.get('pk', None)

        # Return all authors without any restrictions
        authors = Author.objects.all()

        if author_id:
            try:
                author = authors.get(id=author_id)
            except Author.DoesNotExist:
                return Response({"detail": "Author not found."}, status=status.HTTP_404_NOT_FOUND)
            return Response(AuthorSerializer(author).data)

        return Response(AuthorSerializer(authors, many=True).data)

    def post(self, request, *args, **kwargs):
        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            if is_publisher(user):
                serializer.save(status='pending', created_by=user)
            else:
                serializer.save(status='approved', created_by=user)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        author_id = kwargs.get('pk')
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({"detail": "Author not found."}, status=status.HTTP_404_NOT_FOUND)

        # Prevent publisher from approving/rejecting
        if "status" in request.data and not is_admin(request.user):
            return Response({"detail": "Only admin can approve or reject."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = AuthorSerializer(author, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =====================================================================================
#                                   CATEGORY API
# =====================================================================================

class CategoryAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        category_id = kwargs.get('pk', None)

        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
            return Response(CategorySerializer(category).data)

        categories = Category.objects.all()
        return Response(CategorySerializer(categories, many=True).data)

    def post(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        category_id = kwargs.get('pk')
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =====================================================================================
#                                   SUBCATEGORY API
# =====================================================================================

class SubCategoryAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        subcategory_id = kwargs.get('pk', None)

        if subcategory_id:
            try:
                subcategory = SubCategory.objects.get(id=subcategory_id)
            except SubCategory.DoesNotExist:
                return Response({"detail": "SubCategory not found."}, status=status.HTTP_404_NOT_FOUND)
            return Response(SubCategorySerializer(subcategory).data)

        subcategories = SubCategory.objects.all()
        return Response(SubCategorySerializer(subcategories, many=True).data)

    def post(self, request, *args, **kwargs):
        serializer = SubCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        subcategory_id = kwargs.get('pk')
        try:
            subcategory = SubCategory.objects.get(id=subcategory_id)
        except SubCategory.DoesNotExist:
            return Response({"detail": "SubCategory not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubCategorySerializer(subcategory, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =====================================================================================
#                                      BOOK API
# =====================================================================================
class PublicBookAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        book_id = kwargs.get("pk")

        books = Book.objects.filter(status="approved")

        if book_id:
            try:
                book = books.get(id=book_id)
            except Book.DoesNotExist:
                return Response({"detail": "Book not found."},
                                status=status.HTTP_404_NOT_FOUND)

            return Response(BookSerializer(book).data)

        return Response(BookSerializer(books, many=True).data)

class PublisherBookAPIView(APIView):
    permission_classes = [IsPublisher]

    def get(self, request, *args, **kwargs):
        user = request.user
        book_id = kwargs.get("pk")

        books = Book.objects.filter(created_by=user)

        if book_id:
            try:
                book = books.get(id=book_id)
            except Book.DoesNotExist:
                return Response({"detail": "Book not found."}, 
                                status=status.HTTP_404_NOT_FOUND)

            return Response(BookSerializer(book).data)

        return Response(BookSerializer(books, many=True).data)

class AdminBookAPIView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, *args, **kwargs):
        book_id = kwargs.get("pk")

        books = Book.objects.all()

        if book_id:
            try:
                book = books.get(id=book_id)
            except Book.DoesNotExist:
                return Response({"detail": "Book not found."}, 
                                status=status.HTTP_404_NOT_FOUND)

            return Response(BookSerializer(book).data)

        return Response(BookSerializer(books, many=True).data)

# views.py

class PublisherBookCreateAPIView(APIView):
    permission_classes = [IsPublisher]  # Only publishers can access this endpoint

    def post(self, request):
        """
        Handle book creation by a publisher.
        The status will always be set to 'pending' for publishers.
        """
        user = request.user

        # Force the status to 'pending' for publishers, regardless of frontend input
        request.data['status'] = 'pending'

        # Create the book using the provided data, including the overridden status
        serializer = BookSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            # Save the book instance with the modified status
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PublisherBookUpdateAPIView(APIView):
    permission_classes = [IsPublisher]

    def patch(self, request, pk):
        return self._update(request, pk, partial=True)

    def put(self, request, pk):
        return self._update(request, pk, partial=False)

    def _update(self, request, pk, partial):
        user = request.user

        try:
            book = Book.objects.get(id=pk, created_by=user)
        except Book.DoesNotExist:
            return Response({"detail": "Book not found."},
                            status=status.HTTP_404_NOT_FOUND)

        # Publisher CANNOT change status
        if "status" in request.data:
            return Response({"detail": "Publishers cannot modify status."},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = BookSerializer(book, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()  # status and created_by remain unchanged
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# views.py

class AdminBookCreateAPIView(APIView):
    permission_classes = [IsAdmin]  # Only admins can access this endpoint

    def post(self, request):
        """
        Handle book creation by an admin.
        Admin can set any status, as provided by the frontend.
        """
        user = request.user
        serializer = BookSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            # Admin can set any status provided by the frontend
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminBookUpdateAPIView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        return self._update(request, pk, partial=True)

    def put(self, request, pk):
        return self._update(request, pk, partial=False)

    def _update(self, request, pk, partial):
        try:
            book = Book.objects.get(id=pk)
        except Book.DoesNotExist:
            return Response({"detail": "Book not found."},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = BookSerializer(book, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# =====================================================================================
#                                REVIEW API
# =====================================================================================

class ReviewAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        book_id = request.query_params.get('book_id')
        user_id = request.query_params.get('user_id')

        reviews = Review.objects.all()
        if book_id:
            reviews = reviews.filter(book_id=book_id)
        if user_id:
            reviews = reviews.filter(user_id=user_id)

        return Response(ReviewSerializer(reviews, many=True).data)

    def post(self, request, *args, **kwargs):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        review_id = kwargs.get('pk')
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({"detail": "Review not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        review_id = kwargs.get('pk')
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({"detail": "Review not found."}, status=status.HTTP_404_NOT_FOUND)

        review.delete()
        return Response({"detail": "Review deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# =====================================================================================
#                                        STATS API
# =====================================================================================

class StatsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        data = {
            "total_books": Book.objects.count(),
            "total_authors": Author.objects.count(),
            "total_categories": Category.objects.count(),
            "total_subcategories": SubCategory.objects.count(),
            "total_reviews": Review.objects.count(),
        }
        return Response(data, status=status.HTTP_200_OK)

class PublisherBooksAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Only logged-in users

    def get(self, request):
        user = request.user

        # Only allow publishers
        if not hasattr(user, 'role') or user.role != 3:
            return Response({"detail": "Only publishers can access this endpoint."},
                            status=status.HTTP_403_FORBIDDEN)

        # Get books created by this publisher
        books = Book.objects.filter(created_by=user)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PublisherStatsAPIView(APIView):
    permission_classes = [IsPublisher]

    def get(self, request):
        print("Logged in user:", request.user, "Role:", getattr(request.user, 'role', None))
        user = request.user
        data = {
            "total_books": Book.objects.filter(created_by=user).count(),
            "total_reviews": Review.objects.filter(book__created_by=user).count(),
            "total_authors": Author.objects.count(),
            "total_categories": Category.objects.count(),
            "total_subcategories": SubCategory.objects.count(),
        }
        return Response(data, status=status.HTTP_200_OK)
