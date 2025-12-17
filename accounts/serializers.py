from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .models import User,Address

class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'password',
            'role',
        ]
        extra_kwargs = {
            "role": {"required": False},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, data):
        email = data.get('email')
        phone_number = data.get('phone_number')

        if not email and not phone_number:
            raise serializers.ValidationError("Either email or phone number is required.")

        if phone_number:
            if get_user_model().objects.filter(phone_number=phone_number).exists():
                raise serializers.ValidationError("Phone number is already taken.")

        return data

    def create(self, validated_data):
        email = validated_data.get('email')
        phone_number = validated_data.get('phone_number')
        role = validated_data.get('role', 2)  # default: Customer

        username = email if email else phone_number

        # Set is_verified based on role
        if role in [1, 2]:   # Admin or Customer
            is_verified = True
        else:                # Publisher
            is_verified = False

        user = get_user_model().objects.create_user(
            username=username,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=email,
            phone_number=phone_number,
            password=validated_data['password'],
            role=role,
            is_verified=is_verified,
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
        
        if user.is_deleted:
            raise serializers.ValidationError("This account has been deleted.")

        return {
            'user': user,
            'message': "Login successful"
        }

class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'phone_number',
            'first_name',
            'last_name',
            'role',
            'role_display',
            'is_verified'
        ]


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
