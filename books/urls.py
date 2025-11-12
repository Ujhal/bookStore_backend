from django.urls import path
from .views import AuthorAPIView, CategoryAPIView, SubCategoryAPIView, BookAPIView,ReviewAPIView,StatsAPIView

urlpatterns = [
    path('authors/', AuthorAPIView.as_view(), name='author-list-create'),
    path('authors/<int:pk>/', AuthorAPIView.as_view(), name='author-retrieve-update'),
    
    path('categories/', CategoryAPIView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryAPIView.as_view(), name='category-retrieve-update'),
    
    path('subcategories/', SubCategoryAPIView.as_view(), name='subcategory-list-create'),
    path('subcategories/<int:pk>/', SubCategoryAPIView.as_view(), name='subcategory-retrieve-update'),
    
    path('books/', BookAPIView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookAPIView.as_view(), name='book-retrieve-update'),

    path('reviews/', ReviewAPIView.as_view(), name='reviews'),
    path('reviews/<int:pk>/', ReviewAPIView.as_view(), name='review-detail'),
    
    #stats
    path('stats/', StatsAPIView.as_view(), name='stats'),
]
