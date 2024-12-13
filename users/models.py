from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


# UserManager
class UserManager(BaseUserManager):
    """
    Менеджер пользователей для управления кастомной моделью User.
    """

    def get_queryset(self):
        """
        Получить QuerySet всех пользователей.

        Returns:
            QuerySet: QuerySet объектов User.
        """
        return super().get_queryset()

    def create_user(self, email, password=None, **extra_fields):
        """
        Создает обычного пользователя.

        Args:
            email (str): Email пользователя.
            password (str, optional): Пароль пользователя.
            **extra_fields: Дополнительные поля для создания.

        Returns:
            User: Созданный пользователь.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создает суперпользователя.

        Args:
            email (str): Email суперпользователя.
            password (str, optional): Пароль суперпользователя.
            **extra_fields: Дополнительные поля для создания.

        Returns:
            User: Созданный суперпользователь.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# Основная модель пользователя
class User(AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя, расширяющая AbstractBaseUser.

    Атрибуты:
        email (str): Уникальный email пользователя.
        status (str): Статус пользователя (active, suspended).
        is_staff (bool): Является ли пользователь сотрудником.
        is_active (bool): Активен ли пользователь.
        is_verified (bool): Верифицирован ли пользователь.
        created_at (datetime): Дата и время создания.
        updated_at (datetime): Дата и время последнего обновления.
    """

    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=50, default="active")  # active, suspended
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


# Роли пользователей
class Role(models.Model):
    """
    Роль пользователя.

    Атрибуты:
        name (str): Название роли.
    """

    name = models.CharField(max_length=50, unique=True)
    objects = models.Manager()  # Явное объявление менеджера

    def __str__(self):
        return self.name


# # Связь пользователь-роли
# class UserRole(models.Model):
#     """
#     Связь пользователя с ролями.
#
#     Атрибуты:
#         user (User): Связанный пользователь.
#         role (Role): Назначенная роль.
#     """
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     role = models.ForeignKey(Role, on_delete=models.CASCADE)
#     objects = models.Manager()  # Явное объявление менеджера
#
#     def __str__(self):
#         return f"{self.user.email} - {self.role.name}"


class UserProfile(models.Model):
    """
    Профиль пользователя.

    Атрибуты:
        user (User): Связанный пользователь.
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        phone (str): Номер телефона.
        country (str): Страна проживания.
        city (str): Город проживания.
        avatar_url (str): Ссылка на аватар пользователя.
        verification_status (str): Статус верификации профиля.
        role (str): Роль пользователя в системе.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_profiles",
        help_text="Роль пользователя в системе",
    )

    def __str__(self):
        return f"{self.user.email} - {self.verification_status} - {self.role}"


# Верификация пользователя
class UserVerification(models.Model):
    """
    Верификация пользователя.

    Атрибуты:
        user (User): Связанный пользователь.
        document_type (str): Тип документа.
        document_url (str): Ссылка на документ.
        verification_result (str): Результат верификации.
        verified_at (datetime): Дата и время верификации.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="verifications"
    )
    document_type = models.CharField(max_length=50)
    document_url = models.URLField()
    verification_result = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )
    verified_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.verification_result}"
