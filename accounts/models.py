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
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)  # Optional, but unique


    def __str__(self):
        return self.username

# Address model to store the user's address
class Address(models.Model):
    user = models.ForeignKey(User, related_name='addresses', on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)  # Optional second line of address
    landmark = models.CharField(max_length=255, blank=True, null=True)  # Optional landmark
    pincode = models.CharField(max_length=6)  # Assuming 6-digit pincode format
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Optional phone number

    def __str__(self):
        return f"{self.address_line_1}, {self.city}, {self.state}, {self.pincode}"
