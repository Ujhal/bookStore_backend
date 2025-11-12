# myapp/auth_backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

class CustomAuthenticationBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        
        # Try to authenticate by email
        user = None
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            pass

        # If no user found with email, try phone number
        if not user:
            try:
                user = User.objects.get(phone_number=username)
            except User.DoesNotExist:
                pass

        if user and user.check_password(password):
            return user
        return None
