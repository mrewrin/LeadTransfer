from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, UserRole, Role


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=["buyer", "broker"])

    class Meta:
        model = User
        fields = ["email", "password", "role"]

    def create(self, validated_data):
        # Создаем пользователя
        user = User.objects.create_user(
            email=validated_data["email"], password=validated_data["password"]
        )
        # Назначаем выбранную роль
        role_name = validated_data["role"]
        role, created = Role.objects.get_or_create(name=role_name)
        UserRole.objects.create(user=user, role=role)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Добавляем роли пользователя в токен
        roles = [role.role.name for role in user.userrole_set.all()]
        token["roles"] = roles
        return token
