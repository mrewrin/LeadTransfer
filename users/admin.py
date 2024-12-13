from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, Role, UserVerification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Кастомный админ-класс для модели User.
    """

    model = User
    list_display = ("email", "is_staff", "is_active", "is_verified", "created_at")
    list_filter = ("is_staff", "is_active", "is_verified")
    search_fields = ("email",)
    ordering = ("email",)

    # Указание полей для отображения и редактирования
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_active",
                    "is_verified",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Dates", {"fields": ("last_login", "updated_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "is_verified",
                ),
            },
        ),
    )

    # Поля только для чтения
    readonly_fields = ("created_at", "updated_at")


# Регистрация остальных моделей
admin.site.register(UserProfile)
admin.site.register(Role)
admin.site.register(UserVerification)
