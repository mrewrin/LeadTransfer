from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Role, UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователей.

    Позволяет создать нового пользователя и назначить ему выбранную роль.
    """

    password = serializers.CharField(write_only=True, help_text="Пароль пользователя.")
    role = serializers.SlugRelatedField(
        queryset=Role.objects.all(),
        slug_field="name",
        help_text="Роль пользователя (например: admin, broker, buyer).",
    )

    class Meta:
        model = User
        fields = ["email", "password", "role"]
        extra_kwargs = {
            "email": {"help_text": "Email пользователя."},
        }

    def create(self, validated_data):
        """
        Создает пользователя, профиль и назначает ему роль.

        Args:
            validated_data (dict): Проверенные данные из запроса.

        Returns:
            User: Созданный пользователь.
        """
        role = validated_data["role"]
        is_staff = role.name in ["admin", "moderator"]

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            is_staff=is_staff,
        )
        UserProfile.objects.create(user=user, role=role)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Кастомизированный сериализатор для получения JWT-токенов.

    Добавляет роль пользователя в токен.
    """

    @classmethod
    def get_token(cls, user):
        """
        Генерирует токен с дополнительной информацией о ролях пользователя.

        Args:
            user (User): Пользователь, для которого создается токен.

        Returns:
            Token: JWT-токен с дополнительным полем 'role'.
        """
        token = super().get_token(user)
        try:
            profile = user.profile
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
        avatar (ImageField): Поле для загрузки аватара пользователя.
        verification_status (str): Текущий статус верификации профиля.
        role (str): Роль пользователя в системе.
    """

    role = serializers.SlugRelatedField(
        queryset=Role.objects.all(),
        slug_field="name",
        help_text="Роль пользователя (например: admin, broker, buyer).",
    )
    # avatar = serializers.ImageField(
    #     help_text="Загрузка аватара пользователя.", required=False, allow_null=True
    # )
    verification_status = serializers.CharField(
        help_text="Статус верификации профиля пользователя.", read_only=True
    )

    class Meta:
        model = UserProfile
        fields = [
            "first_name",
            "last_name",
            "phone",
            "country",
            "city",
            # "avatar",
            "verification_status",
            "role",
        ]
        read_only_fields = ["verification_status"]

    # @swagger_serializer_method(serializer_or_field=serializers.CharField)
    # def get_role(self, obj):
    #     """
    #     Возвращает роль пользователя в виде строки.
    #
    #     Args:
    #         obj: Экземпляр UserProfile.
    #
    #     Returns:
    #         str: Название роли пользователя.
    #     """
    #     return obj.role.name if obj.role else None
