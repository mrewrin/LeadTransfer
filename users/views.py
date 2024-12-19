from PIL import Image, UnidentifiedImageError
from io import BytesIO
from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
)
from .models import User, UserProfile, UserVerification, Role, RoleAssignmentHistory
from .permissions import IsAdminOrModerator, IsBrokerOrAmbassador


@swagger_auto_schema(
    method="GET",
    operation_summary="Получить защищенный ресурс",
    operation_description="Возвращает защищенный ресурс, если токен пользователя валиден.",
    responses={200: "Успешное сообщение", 401: "Недействительный токен"},
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def protected_view(request):
    """
    Получение защищенного ресурса.
    """
    token = request.auth
    try:
        AccessToken(token).verify()
    except (InvalidToken, TokenError) as e:
        return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({"message": "This is a protected endpoint!"})


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Кастомизированный эндпоинт для получения токенов.
    """

    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(
        operation_summary="Получить JWT токены",
        operation_description="Возвращает access и refresh токены для пользователя.",
        responses={200: "JWT токены", 401: "Ошибка аутентификации"},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RegisterView(APIView):
    """
    Регистрация нового пользователя.
    """

    @swagger_auto_schema(
        operation_summary="Регистрация пользователя",
        operation_description="Создает нового пользователя и назначает ему роль.",
        request_body=RegisterSerializer,
        responses={
            201: "Пользователь успешно зарегистрирован",
            400: "Ошибки валидации",
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": f"User {user.email} registered successfully!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="POST",
    operation_summary="Верифицировать брокера",
    operation_description="Позволяет администратору верифицировать указанного пользователя.",
    responses={200: "Успешная верификация", 404: "Пользователь не найден"},
)
@api_view(["POST"])
@permission_classes([IsAdminUser])
def verify_broker(request, user_id):
    """
    Верификация брокера.
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
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [
        MultiPartParser,
        FormParser,
    ]  # Поддержка обработки multipart-данных

    @swagger_auto_schema(
        operation_summary="Получить профиль пользователя",
        operation_description="Возвращает данные профиля текущего пользователя.",
        responses={200: UserProfileSerializer},
    )
    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Обновить профиль пользователя",
        operation_description="Обновляет данные профиля текущего пользователя.",
        request_body=UserProfileSerializer,
        responses={200: UserProfileSerializer, 400: "Ошибки валидации"},
    )
    def put(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAvatarUploadView(APIView):
    """
    Эндпоинт для загрузки аватара пользователя с автоматической обрезкой.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary="Загрузить аватар",
        operation_description=(
            "Позволяет пользователю загрузить новый аватар.\n\n"
            "Поддерживаемые форматы: JPEG, PNG.\n"
            "Ограничения:\n"
            "- Максимальное разрешение: 512x512 пикселей (автоматическая обрезка).\n"
            "- Максимальный размер файла: 2MB."
        ),
        manual_parameters=[
            openapi.Parameter(
                name="avatar",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description="Файл изображения аватара (JPEG, PNG).",
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                "Аватар успешно обновлен.",
                examples={
                    "application/json": {
                        "message": "Аватар успешно обновлен.",
                        "avatar_url": "/media/avatars/avatar.jpg",
                    }
                },
            ),
            400: "Ошибка загрузки.",
            401: "Необходимо авторизоваться.",
        },
    )
    def post(self, request):
        profile = request.user.profile
        avatar = request.FILES.get("avatar")

        if not avatar:
            return Response(
                {"error": "Файл аватара обязателен."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if avatar.content_type not in ["image/jpeg", "image/png"]:
            return Response(
                {"error": "Только JPEG и PNG файлы поддерживаются."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if avatar.size > 2 * 1024 * 1024:
            return Response(
                {"error": "Размер файла не должен превышать 2MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Открываем изображение
            img = Image.open(avatar)
            max_resolution = (512, 512)

            # Проверяем размеры изображения
            if img.width > max_resolution[0] or img.height > max_resolution[1]:
                left = (img.width - max_resolution[0]) / 2
                top = (img.height - max_resolution[1]) / 2
                right = (img.width + max_resolution[0]) / 2
                bottom = (img.height + max_resolution[1]) / 2
                img = img.crop((left, top, right, bottom))
                img = img.resize(max_resolution)

            buffer = BytesIO()
            img.save(buffer, format=img.format)
            buffer.seek(0)

            file_content = ContentFile(buffer.read(), name=avatar.name)
            profile.avatar.save(avatar.name, file_content, save=True)

        except UnidentifiedImageError:
            return Response(
                {"error": "Файл не является допустимым изображением."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Не удалось обработать изображение: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Аватар успешно обновлен.", "avatar_url": profile.avatar.url},
            status=status.HTTP_200_OK,
        )


class UserVerificationView(APIView):
    """
    Представление для верификации пользователя.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Отправить документы на верификацию",
        operation_description="Принимает тип документа и ссылку "
        "на документ для верификации пользователя.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "document_type": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Тип документа"
                ),
                "document_url": openapi.Schema(
                    type=openapi.TYPE_STRING, description="URL ссылки на документ"
                ),
            },
            required=["document_type", "document_url"],
        ),
        responses={201: "Документ успешно отправлен", 400: "Ошибки валидации"},
    )
    def post(self, request):
        user = request.user
        document_type = request.data.get("document_type")
        document_url = request.data.get("document_url")

        if not document_type or not document_url:
            return Response(
                {"error": "Both document_type and document_url are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

    @swagger_auto_schema(
        operation_summary="Назначить роль пользователю",
        operation_description="Назначает новую роль пользователю по его ID.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "user_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="ID пользователя"
                ),
                "role": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Название роли"
                ),
            },
            required=["user_id", "role"],
        ),
        responses={200: "Роль успешно назначена", 400: "Ошибка запроса"},
    )
    def post(self, request):
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

            profile.role = role
            profile.save()

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

    @swagger_auto_schema(
        operation_summary="Доступ для администратора или модератора",
        operation_description="Возвращает сообщение, если пользователь имеет доступ.",
        responses={200: "Успешное сообщение"},
    )
    def get(self, request):
        return Response({"message": "Welcome, Admin or Moderator!"})


class BrokerOrAmbassadorView(APIView):
    """
    Эндпоинт, доступный только для брокера или амбассадора.
    """

    permission_classes = [IsAuthenticated, IsBrokerOrAmbassador]

    @swagger_auto_schema(
        operation_summary="Доступ для брокера или амбассадора",
        operation_description="Возвращает сообщение, если пользователь имеет доступ.",
        responses={200: "Успешное сообщение"},
    )
    def get(self, request):
        return Response({"message": "Welcome, Broker or Ambassador!"})


class ChangePasswordView(APIView):
    """
    Эндпоинт для смены пароля аутентифицированным пользователем.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Смена пароля",
        operation_description="Позволяет аутентифицированному пользователю сменить пароль.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "old_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Старый пароль"
                ),
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Новый пароль"
                ),
            },
            required=["old_password", "new_password"],
        ),
        responses={
            200: "Пароль успешно изменён",
            400: "Ошибка валидации",
            401: "Неавторизован",
        },
    )
    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response(
                {"error": "Both old_password and new_password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(old_password):
            return Response(
                {"error": "The old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password changed successfully!"}, status=status.HTTP_200_OK
        )
