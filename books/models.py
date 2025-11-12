from django.db import models
from django.utils import timezone
import accounts.models as accounts_model

class Book(models.Model):
    id = models.AutoField(primary_key=True)  # Using AutoField for auto-incrementing integer IDs
    title = models.CharField(max_length=255)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=5, default='INR', null=True, blank=True)
    stock_quantity = models.IntegerField(default=0)
    cover_image = models.BinaryField(blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    publication_date = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=10, default='en', null=True, blank=True)
    pages = models.IntegerField(null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey('SubCategory', on_delete=models.SET_NULL, null=True, blank=True)
    slug = models.SlugField(unique=True, default='temp-slug')  # Provide a default for existing rows
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)  # Ensure default
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)  # Ensure default

    def __str__(self):
        return self.title


class Author(models.Model):
    id = models.AutoField(primary_key=True)  # Using AutoField for auto-incrementing integer IDs
    name = models.CharField(max_length=255)
    biography = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    date_of_death = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    photo = models.BinaryField(blank=True, null=True)  # models. prefix is required here!
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)  # Ensure default
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)  # Ensure default

    def __str__(self):
        return self.name


class Review(models.Model):
    id = models.AutoField(primary_key=True)  # Using AutoField for auto-incrementing integer IDs
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(accounts_model.User, on_delete=models.SET_NULL, null=True)  # assuming you have a User model
    rating = models.PositiveSmallIntegerField()  # e.g. 1 to 5 stars
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('book', 'user')  # one review per user per book

    def __str__(self):
        return f'Review for {self.book.title} by {self.user.username if self.user else "Anonymous"}'


class Category(models.Model):
    id = models.AutoField(primary_key=True)  # Using AutoField for auto-incrementing integer IDs
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    id = models.AutoField(primary_key=True)  # Using AutoField for auto-incrementing integer IDs
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} ({self.category.name})'
