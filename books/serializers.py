import base64
from rest_framework import serializers
from .models import Book, Author, Category, SubCategory, Review

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
        fields = ['id', 'name', 'biography', 'date_of_birth', 'date_of_death', 'nationality', 'photo']

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
            'id', 'title', 'author', 'description', 'price', 'currency', 'stock_quantity',
            'cover_image', 'publisher', 'publication_date', 'language', 'pages', 'category', 
            'subcategory', 'slug', 'created_at', 'updated_at','category_name', 'author_name',              # <--- add category_name here
            'subcategory_name'
        ]

    def validate_slug(self, value):
        if self.instance:
            if Book.objects.exclude(id=self.instance.id).filter(slug=value).exists():
                raise serializers.ValidationError("Slug must be unique.")
        else:
            if Book.objects.filter(slug=value).exists():
                raise serializers.ValidationError("Slug must be unique.")
        return value

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'book', 'user', 'rating', 'comment', 'created_at', 'updated_at']
