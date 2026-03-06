from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import generics, permissions
from .models import Address,User,State
from django.db.models import Q
 

from django.db.models.functions import Cast
from django.db.models import CharField
from rest_framework_simplejwt.views import TokenObtainPairView
from .tokens import MyTokenObtainPairSerializer

from .serializers import UserRegistrationSerializer, LoginSerializer,UserSerializer,AddressSerializer,StateSerializer



# User Registration View
class UserRegistrationView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # Create the user
            # Optionally, you can create an auth token for the user here
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        login_data = request.data.get('loginData', {})
        serializer = LoginSerializer(data=login_data)

        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            user_data = UserSerializer(user).data

            return Response({
                'user': user_data,
                'message': serializer.validated_data['message'],
                'access_token': access_token,
                'refresh_token': refresh_token
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]  # Make sure user is authenticated

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  


# Retrieve, update, or delete a single address
class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)



class PublisherListView(generics.ListAPIView):
    permission_classes = [AllowAny]  # or IsAuthenticated
    serializer_class = UserSerializer

    def get_queryset(self):
        # Cast role (int) → string so it can match varchar column in database
        return (
            User.objects
            .annotate(role_str=Cast("role", CharField()))
            .filter(role_str="3")
        )


class SelfDeleteUserView(views.APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.is_deleted = True
        user.is_active = False  # optional but recommended
        user.save()

        return Response(
            {"message": "Your account has been deleted successfully."},
            status=status.HTTP_200_OK
        )
        
class AdminDeleteUserView(views.APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        if request.user.role != 1:
            return Response(
                {"error": "Only admin can delete users."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            user = User.objects.get(id=user_id, is_deleted=False)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found or already deleted."},
                status=status.HTTP_404_NOT_FOUND
            )

        user.is_deleted = True
        user.is_active = False
        user.save()

        return Response(
            {"message": "User deleted successfully."},
            status=status.HTTP_200_OK
        )
        
class MyProfileView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.is_deleted:
            return Response(
                {"error": "Account deleted"},
                status=403
            )

        serializer = UserSerializer(user)
        return Response(serializer.data)        

# Custom permission
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access for any user.
    Write access (POST, PATCH, DELETE) only for admin (role=1).
    """
    def has_permission(self, request, view):
        # Safe methods are GET, HEAD, OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow admin (role=1) for unsafe methods
        return hasattr(request.user, 'role') and request.user.role == 1

class StateListView(generics.ListCreateAPIView):
    queryset = State.objects.filter(is_active=True).order_by('name')
    serializer_class = StateSerializer
    permission_classes = [IsAdminOrReadOnly]

    # Optional: override delete for admin check if needed on individual objects
    def delete(self, request, *args, **kwargs):
        if not hasattr(request.user, 'role') or request.user.role != 1:
            return Response(
                {"error": "Only admin can delete states."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)