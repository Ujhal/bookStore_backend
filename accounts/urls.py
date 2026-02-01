from django.urls import path
from .views import UserRegistrationView, LoginView,AddressDetailView,AddressListCreateView, PublisherListView,AdminDeleteUserView,SelfDeleteUserView,MyProfileView,StateListView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),

    path('addresses/', AddressListCreateView.as_view(), name='address-list-create'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),

    path('publishers/', PublisherListView.as_view(), name='publisher-list'),
    
    path('admin/delete-user/<int:user_id>/', AdminDeleteUserView.as_view()),
    path('users/delete-self/', SelfDeleteUserView.as_view()),

    path('states/', StateListView.as_view(), name='state-list'),




    path('me/', MyProfileView.as_view(), name='my-profile'),

]
