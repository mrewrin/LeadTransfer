from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Role, UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователей.

    Позволяет создать нового пользователя и назначить ему выбранную роль.
    """

    password = serializers.CharField(write_only=True)
    role = serializers.SlugRelatedField(
        queryset=Role.objects.all(), slug_field="name"
    )  # Используем SlugRelatedField для связи с ролями

    class Meta:
        model = User
        fields = ["email", "password", "role"]

    def create(self, validated_data):
        """
        Создает пользователя, профиль и назначает ему роль.

        Args:
            validated_data (dict): Проверенные данные из запроса.

        Returns:
            User: Созданный пользователь.
        """

        # Создаем пользователя
        role = validated_data["role"]
        is_staff = role.name in ["admin", "moderator"]

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            is_staff=is_staff,  # Указываем флаг is_staff
        )
        # Создаем профиль пользователя и связываем с ролью
        UserProfile.objects.create(user=user, role=role)

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Кастомизированный сериализатор для получения JWT-токенов.

    Добавляет список ролей пользователя в токен.
    """

    @classmethod
    def get_token(cls, user):
        """
        Генерирует токен с дополнительной информацией о ролях пользователя.

        Args:
            user (User): Пользователь, для которого создается токен.

        Returns:
            Token: JWT-токен с дополнительным полем 'roles'.
        """
        token = super().get_token(user)
        # Добавляем роль пользователя из UserProfile
        try:
            profile = user.profile  # Связь OneToOne
            token["role"] = profile.role.name if profile.role else None
        except UserProfile.DoesNotExist:
            token["role"] = None
        return token


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для профиля пользователя.

    Поля:
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        phone (str): Номер телефона пользователя.
        country (str): Страна проживания пользователя.
        city (str): Город проживания пользователя.
        avatar_url (str): Ссылка на аватар пользователя.
        verification_status (str): Текущий статус верификации профиля.
        role (str): Роль пользователя в системе.
    """

    role = serializers.SlugRelatedField(
        queryset=Role.objects.all(),
        slug_field="name",  # Используем название роли для удобства
    )

    class Meta:
        model = UserProfile
        fields = [
            "first_name",
            "last_name",
            "phone",
            "country",
            "city",
            "avatar_url",
            "verification_status",
            "role",
        ]
        read_only_fields = ["verification_status"]
