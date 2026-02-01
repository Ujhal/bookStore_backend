from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User model
class User(AbstractUser):
    ROLE_CHOICES = (
        (1, 'Admin'),
        (2, 'Customer'),
        (3, 'Publisher'),
        
    )

    # Custom role field to specify the user's role
    role = models.IntegerField(
    choices=ROLE_CHOICES,
    default=2  # Customer
)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)




    def __str__(self):
        return self.username

class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

# Address model to store the user's address
class Address(models.Model):
    user = models.ForeignKey(User, related_name='addresses', on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)  # Optional second line of address
    landmark = models.CharField(max_length=255, blank=True, null=True)  # Optional landmark
    pincode = models.CharField(max_length=6)  # Assuming 6-digit pincode format
    city = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Optional phone number
    state = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        related_name='addresses',
        default=1  # <-- ID of "Unknown" state
    )

    def __str__(self):
        return f"{self.address_line_1}, {self.city}, {self.state.name}, {self.pincode}"


