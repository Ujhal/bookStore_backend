from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .models import User,Address,State
from django.db.models import Q

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

        errors = {}

        # Require either email or phone
        if not email and not phone_number:
            raise serializers.ValidationError(
                {"non_field_errors": ["Either email or phone number is required."]}
            )

        # Check email uniqueness
        if email and get_user_model().objects.filter(email=email).exists():
            errors["email"] = ["Email is already registered."]

        # Check phone uniqueness
        if phone_number and get_user_model().objects.filter(phone_number=phone_number).exists():
            errors["phone_number"] = ["Phone number is already registered."]

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        email = validated_data.get('email')
        phone_number = validated_data.get('phone_number')
        role = validated_data.get('role', 2)  # default: Customer

        username = email if email else phone_number

        # Auto verification logic
        is_verified = True if role in [1, 2] else False

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
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Check if user exists by email or phone number
        try:
            user = User.objects.get(Q(email=username) | Q(phone_number=username))
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email or phone number.")

        if user.is_deleted:
            raise serializers.ValidationError("This account has been deleted.")

        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")

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
    state_name = serializers.ReadOnlyField(source='state.name')
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
            'state_name', 
            'phone_number',
        ]
        read_only_fields = ['id', 'user']


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name', 'code']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context['request'].user

        # Check old password
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})

        # Check new password match
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        return data        

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone_number = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        phone_number = data.get("phone_number")

        try:
            user = User.objects.get(email=email, phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"error": "User with this email and phone number not found."}
            )

        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        data["user"] = user
        return data