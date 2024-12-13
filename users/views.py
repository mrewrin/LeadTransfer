# from django.core.mail import send_mail  # Для отправки писем
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
)
from .models import User, UserProfile, UserVerification, Role, RoleAssignmentHistory
from .permissions import IsAdminOrModerator, IsBrokerOrAmbassador


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def protected_view(request):
    """
    Получение защищенного ресурса.
    """
    token = request.auth
    try:
        AccessToken(token).verify()  # Явная проверка токена
    except InvalidToken as e:
        return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    except TokenError as e:
        return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({"message": "This is a protected endpoint!"})


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Кастомизированный эндпоинт для получения токенов.

    Использует `CustomTokenObtainPairSerializer` для обработки данных
    и генерации JWT токенов.
    """

    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    """
    Регистрация нового пользователя.

    Эндпоинт для создания нового пользователя. При успешной регистрации
    возвращает сообщение об успешной операции. В дальнейшем можно добавить
    функционал отправки подтверждающего email.
    """

    def post(self, request):
        """
        Создание нового пользователя.

        Args:
            request: HTTP-запрос, содержащий данные для регистрации.

        Returns:
            Response: Сообщение об успешной регистрации или ошибки валидации.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Заготовка для отправки email (пока не активирована)
            # send_mail(
            #     'Подтверждение регистрации',
            #     'Ссылка для подтверждения: http://example.com/confirm',
            #     settings.DEFAULT_FROM_EMAIL,
            #     [user.email],
            # )
            return Response(
                {"message": f"User {user.email} registered successfully!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def verify_broker(request, user_id):
    """
    Верификация брокера.

    Доступно только для администраторов. Устанавливает флаг верификации
    (`is_verified`) для указанного пользователя по его `user_id`.

    Args:
        request: HTTP-запрос от администратора.
        user_id: ID пользователя, который должен быть верифицирован.

    Returns:
        Response: Сообщение об успешной операции или ошибка, если пользователь не найден.
    """
    try:
        user = User.objects.get(id=user_id)
        user.is_verified = True
        user.save()
        return Response({"message": "Broker verified successfully!"})
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)


class UserProfileView(APIView):
    """
    Представление для работы с профилем пользователя.

    Методы:
        get: Возвращает данные профиля текущего пользователя.
        put: Обновляет данные профиля текущего пользователя.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Получить данные профиля пользователя.

        Возвращает текущие данные профиля пользователя, включая его роль.

        Возвращаемые данные:
            Response: JSON-данные профиля.
        """
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        """
        Обновить данные профиля пользователя.

        Принимает данные для обновления и обновляет профиль, включая роль.

        Возвращаемые данные:
            Response: Обновленные данные профиля или ошибки валидации.
        """
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserVerificationView(APIView):
    """
    Представление для верификации пользователя.

    Методы:
        post: Отправляет документы пользователя на проверку.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Отправить документы на проверку.

        Данные запроса:
            document_type (str): Тип документа.
            document_url (str): URL документа.

        Возвращаемые данные:
            Response: Успешный статус или ошибки валидации.
        """
        user = request.user
        document_type = request.data.get("document_type")
        document_url = request.data.get("document_url")

        if not document_type or not document_url:
            return Response(
                {"error": "Both document_type and document_url are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Создание записи о верификации
        verification = UserVerification.objects.create(
            user=user.profile.user,
            document_type=document_type,
            document_url=document_url,
        )
        return Response(
            {"message": "Document submitted for verification", "id": verification.id},
            status=status.HTTP_201_CREATED,
        )


class AssignRoleView(APIView):
    """
    Эндпоинт для назначения ролей пользователям.
    """

    permission_classes = [IsAuthenticated, IsAdminOrModerator]

    def post(self, request):
        """
        Назначение роли пользователю.

        Данные запроса:
            user_id (int): ID пользователя.
            role (str): Название роли.

        Возвращаемые данные:
            Response: Сообщение об успешной операции или ошибки.
        """
        user_id = request.data.get("user_id")
        role_name = request.data.get("role")

        if not user_id or not role_name:
            return Response(
                {"error": "Both user_id and role are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            profile = UserProfile.objects.get(user_id=user_id)
            role = Role.objects.filter(name=role_name).first()
            if not role:
                return Response(
                    {"error": f"Role '{role_name}' does not exist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Назначаем новую роль
            profile.role = role
            profile.save()

            # Логируем изменение роли
            RoleAssignmentHistory.objects.create(
                user=profile.user,
                assigned_by=request.user,
                role=role,
            )

            return Response(
                {
                    "message": f"Role '{role.name}' assigned to user {profile.user.email}."
                },
                status=status.HTTP_200_OK,
            )

        except UserProfile.DoesNotExist:
            return Response(
                {"error": "UserProfile not found for the given user_id."},
                status=status.HTTP_404_NOT_FOUND,
            )


class AdminOrModeratorView(APIView):
    """
    Эндпоинт, доступный только для администратора или модератора.
    """

    permission_classes = [IsAuthenticated, IsAdminOrModerator]

    def get(self, request):
        """
        Возвращает сообщение, если пользователь имеет доступ.

        Returns:
            Response: Успешное сообщение.
        """
        return Response({"message": "Welcome, Admin or Moderator!"})


class BrokerOrAmbassadorView(APIView):
    """
    Эндпоинт, доступный только для брокера или амбассадора.
    """

    permission_classes = [IsAuthenticated, IsBrokerOrAmbassador]

    def get(self, request):
        """
        Возвращает сообщение, если пользователь имеет доступ.

        Returns:
            Response: Успешное сообщение.
        """
        return Response({"message": "Welcome, Broker or Ambassador!"})
