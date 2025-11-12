from django.contrib import admin
from .models import Book, Author, Category, SubCategory, Review


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_of_birth', 'date_of_death', 'nationality')
    search_fields = ('name', 'biography')
    list_filter = ('nationality', 'date_of_birth', 'date_of_death')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    list_filter = ('name',)


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description')
    search_fields = ('name', 'category__name',)
    list_filter = ('category',)


class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'price', 'stock_quantity', 'publisher', 'publication_date', 'language', 'category', 'subcategory', 'slug', 'created_at', 'updated_at'
    )
    search_fields = ('title', 'author__name', 'publisher', 'category__name', 'subcategory__name', 'slug')
    list_filter = ('author', 'category', 'subcategory', 'publisher', 'language')
    prepopulated_fields = {'slug': ('title',)}  # Automatically generate slug from the title


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'created_at')
    search_fields = ('book__title', 'user__username', 'comment')
    list_filter = ('rating', 'created_at')


# Register models with the admin site
admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Review, ReviewAdmin)
