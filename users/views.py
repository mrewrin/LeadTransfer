from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
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
