from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    # You can add additional fields here if needed
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)   
    phone_number = models.CharField(max_length=15, null=True, blank=True)   
    
    pass
    def __str__(self):
        return self.username