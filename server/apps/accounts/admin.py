from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    ordering = ("email",)
    list_display = ("email", "role", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    fieldsets = ((None, {"fields": ("email", "password")}), ("Personal info", {"fields": ("first_name", "last_name", "role")}), ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}))
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "role", "is_staff", "is_active")}),)
