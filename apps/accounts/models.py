from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('librarian', 'Librarian'),
        ('member', 'Member'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='member')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    membership_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    current_books_borrowed = models.IntegerField(default=0)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.username} - {self.get_user_type_display()}"
