from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .models import User,Address

class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)  # Email is optional
    phone_number = serializers.CharField(max_length=15, required=False)  # Phone number is optional, but must be unique if provided
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()  # This gets the custom User model
        fields = ['email', 'phone_number', 'password', 'role']

    def validate(self, data):
        email = data.get('email')
        phone_number = data.get('phone_number')

        # At least one of email or phone number must be provided
        if not email and not phone_number:
            raise serializers.ValidationError("Either email or phone number is required.")

        # Check if phone number is unique (if provided)
        if phone_number:
            if get_user_model().objects.filter(phone_number=phone_number).exists():
                raise serializers.ValidationError("Phone number is already taken.")

        return data

    def create(self, validated_data):
        email = validated_data.get('email')
        phone_number = validated_data.get('phone_number')
        
        if email:
            username = email  # Use email as username
        else:
            username = phone_number  # Use phone number as username

        user = get_user_model().objects.create_user(
            username=username,  # Using phone number or email as username
            email=email,
            phone_number=phone_number,
            password=validated_data['password'],
            role=validated_data.get('role', 'Customer'),
        )
        return user



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()  # username can be email or phone number
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Try authenticating with the username (email or phone number) and password
        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials.")

        return {
            'user': user,
            'message': "Login successful"
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'role']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id',
            'user',
            'address_line_1',
            'address_line_2',
            'landmark',
            'pincode',
            'city',
            'state',
            'phone_number',
        ]
        read_only_fields = ['id', 'user']
