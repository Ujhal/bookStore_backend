from django.urls import path
from .views import UserRegistrationView, LoginView,AddressDetailView,AddressListCreateView, PublisherListView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),

    path('addresses/', AddressListCreateView.as_view(), name='address-list-create'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),

    path('publishers/', PublisherListView.as_view(), name='publisher-list'),
    
]
