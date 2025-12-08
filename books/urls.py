from django.urls import path
from .views import (
    AuthorUpdateAPIView,
    AuthorListCreateAPIView,
    CategoryAPIView,
    SubCategoryAPIView,

    AdminBookAPIView,
    AdminBookCreateAPIView,
    AdminBookUpdateAPIView,

    ReviewAPIView,
    StatsAPIView,

    PublisherBooksAPIView,  # New publisher dashboard endpoint
    PublisherStatsAPIView,
    PublicBookAPIView,
    
    PublisherBookAPIView,
    PublisherBookCreateAPIView,
    PublisherBookUpdateAPIView,
)

urlpatterns = [
    # Author Endpoints
    path('authors/', AuthorListCreateAPIView.as_view(), name='author-list-create'),
    path('authors/<int:pk>/', AuthorUpdateAPIView.as_view(), name='author-detail-update'),

    # Category Endpoints
    path('categories/', CategoryAPIView.as_view(), name='categories-list-create'),
    path('categories/<int:pk>/', CategoryAPIView.as_view(), name='categories-detail'),

    # SubCategory Endpoints
    path('subcategories/', SubCategoryAPIView.as_view(), name='subcategories-list-create'),
    path('subcategories/<int:pk>/', SubCategoryAPIView.as_view(), name='subcategories-detail'),

    # Book Endpoints
    #path('books/', BookAPIView.as_view(), name='books-list-create'),
    #path('books/<int:pk>/', BookAPIView.as_view(), name='books-detail'),

    # Review Endpoints
    path('reviews/', ReviewAPIView.as_view(), name='reviews-list-create'),
    path('reviews/<int:pk>/', ReviewAPIView.as_view(), name='reviews-detail'),

    # Stats Endpoint
    path('stats/', StatsAPIView.as_view(), name='stats'),
    path('PublisherStats/', PublisherStatsAPIView.as_view(), name='stats'),


    # Publisher Dashboard Endpoint 
    #path('publisher/books/', PublisherBooksAPIView.as_view(), name='publisher-books'),

    # PUBLIC
    path("books/", PublicBookAPIView.as_view()),
    path("books/<int:pk>/", PublicBookAPIView.as_view()),

    # PUBLISHER
    path("publisher/books/", PublisherBookAPIView.as_view()),
    path("publisher/books/<int:pk>/", PublisherBookAPIView.as_view()),

    # POST: create pending books
    path("publisher/books/create/", PublisherBookCreateAPIView.as_view(),
         name="publisher-book-create"),

    # PUT/PATCH: update own books (status not allowed)
    path("publisher/books/<int:pk>/update/", PublisherBookUpdateAPIView.as_view(),
         name="publisher-book-update"),

    # ADMIN
    path("admin/books/", AdminBookAPIView.as_view()),
    path("admin/books/<int:pk>/", AdminBookAPIView.as_view()),

     # POST: create approved books
    path("admin/books/create/", AdminBookCreateAPIView.as_view(),
         name="admin-book-create"),

    # PUT/PATCH: update any book + approve
    path("admin/books/<int:pk>/update/", AdminBookUpdateAPIView.as_view(),
         name="admin-book-update"),
         
]
