import base64
from rest_framework import serializers
from .models import Book, Author, Category, SubCategory, Review
import logging

# Set up logging
logger = logging.getLogger(__name__)

class Base64BinaryField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, str):
            if "base64," in data:
                header, data = data.split("base64,", 1)
            try:
                decoded_file = base64.b64decode(data)
            except Exception:
                raise serializers.ValidationError("Invalid base64-encoded data")
            return decoded_file
        raise serializers.ValidationError("Invalid type. Expected a base64 string.")

    def to_representation(self, value):
        if value is None:
            return None
        encoded = base64.b64encode(value).decode('utf-8')
        return f"data:image/png;base64,{encoded}"

class AuthorSerializer(serializers.ModelSerializer):
    photo = Base64BinaryField(required=False, allow_null=True)

    class Meta:
        model = Author
        fields = [
                    'id', 'name', 'biography', 'date_of_birth', 'date_of_death',
                    'nationality', 'photo', 'status', 'created_by'
                ]
        read_only_fields = ['status', 'created_by']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class SubCategorySerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'description', 'category', 'category_name']



class BookSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    author_name = serializers.CharField(source='author.name', read_only=True)

    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    category_name = serializers.CharField(source='category.name', read_only=True)

    subcategory = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all())
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)

    cover_image = Base64BinaryField(required=False, allow_null=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'description', 'price', 'currency',
            'stock_quantity', 'cover_image', 'publisher', 'publication_date',
            'language', 'pages', 'category', 'subcategory', 'slug',
            'status', 'created_by', 'created_at', 'updated_at',
            'author_name', 'category_name', 'subcategory_name','status','is_publisher',
        ]
        read_only_fields = ['created_by', 'author_name', 'category_name', 'subcategory_name']

   

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'book', 'user', 'rating', 'comment', 'created_at', 'updated_at']
