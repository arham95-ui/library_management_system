from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_active', 'current_books_borrowed')
    list_filter = ('user_type', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('user_type', 'phone', 'address', 'profile_picture', 'membership_date', 'current_books_borrowed', 'fine_amount')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
