from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'phone_number', 'preferred_language', 'is_premium', 'is_staff')
    list_filter = ('is_premium', 'preferred_language', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations KIRA', {
            'fields': ('phone_number', 'preferred_language', 'is_premium'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations KIRA', {
            'fields': ('phone_number', 'preferred_language', 'is_premium'),
        }),
    )


admin.site.register(User, CustomUserAdmin)