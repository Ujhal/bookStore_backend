from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import generics, permissions
from .models import Address


from .serializers import UserRegistrationSerializer, LoginSerializer,UserSerializer,AddressSerializer

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

            # Generate refresh and access tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            user_data = UserSerializer(user).data  # serialize user info safely

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
