from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Author, Category, SubCategory, Book
from .serializers import AuthorSerializer, CategorySerializer, SubCategorySerializer, BookSerializer
from rest_framework.permissions import AllowAny
from django.db.models import Count
from .models import Book, Author, Category, SubCategory, Review


# Author API View
class AuthorAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        author_id = kwargs.get('pk', None)
        if author_id:
            try:
                author = Author.objects.get(id=author_id)
            except Author.DoesNotExist:
                return Response({"detail": "Author not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = AuthorSerializer(author)
            return Response(serializer.data)
        else:
            authors = Author.objects.all()
            serializer = AuthorSerializer(authors, many=True)
            return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        author_id = kwargs.get('pk')
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({"detail": "Author not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AuthorSerializer(author, data=request.data, partial=False)  # Full update
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        author_id = kwargs.get('pk')
        try:
            author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            return Response({"detail": "Author not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AuthorSerializer(author, data=request.data, partial=True)  # Partial update
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Category API View
class CategoryAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        category_id = kwargs.get('pk', None)
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        else:
            categories = Category.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        category_id = kwargs.get('pk')
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
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


# SubCategory API View
class SubCategoryAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        subcategory_id = kwargs.get('pk', None)
        if subcategory_id:
            try:
                subcategory = SubCategory.objects.get(id=subcategory_id)
            except SubCategory.DoesNotExist:
                return Response({"detail": "SubCategory not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = SubCategorySerializer(subcategory)
            return Response(serializer.data)
        else:
            subcategories = SubCategory.objects.all()
            serializer = SubCategorySerializer(subcategories, many=True)
            return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = SubCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        subcategory_id = kwargs.get('pk')
        try:
            subcategory = SubCategory.objects.get(id=subcategory_id)
        except SubCategory.DoesNotExist:
            return Response({"detail": "SubCategory not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubCategorySerializer(subcategory, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
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


# Book API View
class BookAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        book_id = kwargs.get('pk', None)
        if book_id:
            try:
                book = Book.objects.get(id=book_id)
            except Book.DoesNotExist:
                return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
            serializer = BookSerializer(book)
            return Response(serializer.data)
        else:
            books = Book.objects.all()
            serializer = BookSerializer(books, many=True)
            return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        book_id = kwargs.get('pk')
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = BookSerializer(book, data=request.data, partial=False)  # Full update
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        book_id = kwargs.get('pk')
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"detail": "Book not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = BookSerializer(book, data=request.data, partial=True)  # Partial update
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ReviewAPIView(APIView):
    """
    Manage book reviews — create, update, delete, and view.
    """
    permission_classes = [AllowAny]  # Change to [IsAuthenticatedOrReadOnly] if login is needed

    def get(self, request, *args, **kwargs):
        """
        Get all reviews or filter by book_id or user_id
        Example: /api/reviews/?book_id=3
        """
        book_id = request.query_params.get('book_id')
        user_id = request.query_params.get('user_id')

        reviews = Review.objects.all()

        if book_id:
            reviews = reviews.filter(book_id=book_id)
        if user_id:
            reviews = reviews.filter(user_id=user_id)

        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Create a new review
        Required fields: book, user, rating
        """
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        """
        Update an existing review (full update)
        """
        review_id = kwargs.get('pk')
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({"detail": "Review not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewSerializer(review, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        """
        Partially update a review
        """
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
        """
        Delete a review by ID
        """
        review_id = kwargs.get('pk')
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({"detail": "Review not found."}, status=status.HTTP_404_NOT_FOUND)

        review.delete()
        return Response({"detail": "Review deleted successfully."}, status=status.HTTP_204_NO_CONTENT)




class StatsAPIView(APIView):
    """
    Returns overall stats about books, authors, categories, etc.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # Count total items
        total_books = Book.objects.count()
        total_authors = Author.objects.count()
        total_categories = Category.objects.count()
        total_subcategories = SubCategory.objects.count()
        total_reviews = Review.objects.count()

        # Count books category-wise
        category_wise_books = (
            Category.objects
            .annotate(book_count=Count('book'))
            .values('id', 'name', 'book_count')
        )

        # If you also want subcategory-wise counts
        subcategory_wise_books = (
            SubCategory.objects
            .annotate(book_count=Count('book'))
            .values('id', 'name', 'category__name', 'book_count')
        )

        data = {
            "total_books": total_books,
            "total_authors": total_authors,
            "total_categories": total_categories,
            "total_subcategories": total_subcategories,
            "total_reviews": total_reviews,
            "category_wise_books": list(category_wise_books),
            "subcategory_wise_books": list(subcategory_wise_books)
        }

        return Response(data, status=status.HTTP_200_OK)
