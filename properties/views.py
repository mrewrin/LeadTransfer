from django.core.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_200_OK
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Catalog, RealEstateObject
from .serializers import ObjectSerializer, CatalogSerializer
from users.permissions import IsAdminOrBroker


class ObjectListCreateView(ListCreateAPIView):
    """
    API представление для получения списка объектов недвижимости и их создания.
    """

    queryset = RealEstateObject.objects.all()
    serializer_class = ObjectSerializer

    @swagger_auto_schema(
        operation_summary="Получить список объектов недвижимости",
        operation_description="Возвращает список объектов недвижимости "
        "с фильтрацией по цене, статусу и стране.",
        manual_parameters=[
            openapi.Parameter(
                "price_min",
                openapi.IN_QUERY,
                description="Минимальная цена объекта",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "price_max",
                openapi.IN_QUERY,
                description="Максимальная цена объекта",
                type=openapi.TYPE_NUMBER,
            ),
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Статус объекта (sale, rent, sold)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "country",
                openapi.IN_QUERY,
                description="Страна расположения объекта",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: ObjectSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создать новый объект недвижимости",
        operation_description="Создает новый объект недвижимости. "
        "Доступно только для брокеров и администраторов.",
        request_body=ObjectSerializer,
        responses={201: ObjectSerializer, 400: "Ошибки валидации"},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_serializer_context(self):
        """
        Добавляет текущий запрос в контекст сериализатора.
        """
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        """
        Привязывает текущего пользователя как брокера при создании объекта недвижимости.
        """
        serializer.save(broker=self.request.user)

    def perform_update(self, serializer):
        """
        Проверка прав при обновлении и сохранение данных.
        """
        if (
            self.request.user != serializer.instance.broker
            and not self.request.user.is_superuser
        ):
            raise PermissionDenied("Вы можете изменять только свои объекты.")

        # Полное обновление требует все обязательные поля
        if not self.request.data.get("country") or not self.request.data.get("city"):
            raise ValidationError("Все обязательные поля должны быть заполнены.")

        serializer.save()

    def get_queryset(self):
        queryset = super().get_queryset()
        try:
            price_min = self.request.query_params.get("price_min")
            price_max = self.request.query_params.get("price_max")
            if price_min:
                queryset = queryset.filter(price__gte=float(price_min))
            if price_max:
                queryset = queryset.filter(price__lte=float(price_max))
        except ValueError:
            raise ValidationError(
                "Параметры price_min и price_max должны быть числами."
            )

        status = self.request.query_params.get("status")
        country = self.request.query_params.get("country")
        if status:
            queryset = queryset.filter(status=status)
        if country:
            queryset = queryset.filter(country__icontains=country)

        return queryset

    def get_permissions(self):
        if self.request.method in ["POST"]:
            return [IsAdminOrBroker()]
        return [AllowAny()]


class ObjectDetailView(RetrieveUpdateDestroyAPIView):
    """
    API представление для детального просмотра, обновления и удаления объекта недвижимости.
    """

    queryset = RealEstateObject.objects.all()
    serializer_class = ObjectSerializer

    @swagger_auto_schema(
        operation_summary="Получить детали объекта недвижимости",
        operation_description="Возвращает подробную информацию об объекте недвижимости.",
        responses={200: ObjectSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновить объект недвижимости",
        operation_description="Обновляет данные объекта недвижимости. "
        "Доступно только владельцу объекта или администратору.",
        request_body=ObjectSerializer,
        responses={200: ObjectSerializer, 403: "Доступ запрещен"},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удалить объект недвижимости",
        operation_description="Удаляет объект недвижимости. "
        "Доступно только владельцу объекта или администратору.",
        responses={204: "Объект успешно удален", 403: "Доступ запрещен"},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance):
        if self.request.user != instance.broker and not self.request.user.is_superuser:
            raise PermissionDenied("Вы можете удалять только свои объекты.")
        instance.delete()

    def perform_update(self, serializer):
        if (
            self.request.user != serializer.instance.broker
            and not self.request.user.is_superuser
        ):
            raise PermissionDenied("Вы можете изменять только свои объекты.")
        serializer.save()

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminOrBroker()]
        return [AllowAny()]


class CatalogListCreateView(ListCreateAPIView):
    """
    API представление для получения списка каталогов и их создания.
    """

    queryset = Catalog.objects.all()
    serializer_class = CatalogSerializer

    @swagger_auto_schema(
        operation_summary="Получить список каталогов",
        operation_description="Возвращает список каталогов с возможностью фильтрации по владельцу.",
        manual_parameters=[
            openapi.Parameter(
                "owner",
                openapi.IN_QUERY,
                description="ID владельца каталога",
                type=openapi.TYPE_INTEGER,
            )
        ],
        responses={200: CatalogSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Создать новый каталог",
        operation_description="Создает новый каталог и привязывает его к текущему пользователю.",
        request_body=CatalogSerializer,
        responses={201: CatalogSerializer, 400: "Ошибки валидации"},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Привязываем текущего пользователя как владельца каталога
        serializer.save(broker=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_public=True)
        return queryset

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminOrBroker()]
        return [AllowAny()]  # GET-запросы доступны всем


class CatalogDetailView(RetrieveUpdateDestroyAPIView):
    """
    API представление для детального просмотра, обновления и удаления каталога.

    Права доступа:
        - GET: Публичные каталоги доступны всем.
          Приватные каталоги доступны только владельцу и администраторам.
        - PUT, PATCH, DELETE: Доступ разрешён только владельцу каталога и администраторам.
    """

    queryset = Catalog.objects.all()
    serializer_class = CatalogSerializer

    def get_queryset(self):
        """
        Возвращает все каталоги (публичные и приватные) для дальнейшей обработки.
        """
        return Catalog.objects.all()  # Включаем все каталоги

    @swagger_auto_schema(
        operation_summary="Получить детали каталога",
        operation_description=(
            "Возвращает подробную информацию о каталоге.\n\n"
            "Доступ:\n"
            "- Публичные каталоги доступны всем пользователям.\n"
            "- Приватные каталоги доступны только владельцу или администраторам."
        ),
        responses={
            200: CatalogSerializer,
            403: openapi.Response("Доступ к этому каталогу запрещен."),
        },
    )
    def get(self, request, *args, **kwargs):
        """
        Обработка GET-запроса для получения деталей каталога.
        """
        catalog = self.get_object()
        if not catalog.is_public and (
            not request.user.is_authenticated or request.user != catalog.broker
        ):
            return Response(
                {"detail": "Доступ к этому каталогу запрещен."},
                status=HTTP_403_FORBIDDEN,
            )
        return Response(self.get_serializer(catalog).data, status=HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Обновить каталог",
        operation_description=(
            "Обновляет данные каталога.\n\n"
            "Доступ разрешён только владельцу каталога или администраторам."
        ),
        request_body=CatalogSerializer,
        responses={
            200: CatalogSerializer,
            403: openapi.Response("Вы можете изменять только свои каталоги."),
        },
    )
    def put(self, request, *args, **kwargs):
        """
        Обработка PUT-запроса для обновления каталога.
        """
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удалить каталог",
        operation_description=(
            "Удаляет существующий каталог.\n\n"
            "Доступ разрешён только владельцу каталога или администраторам."
        ),
        responses={
            204: openapi.Response("Каталог успешно удален."),
            403: openapi.Response("Вы можете удалять только свои каталоги."),
        },
    )
    def delete(self, request, *args, **kwargs):
        """
        Обработка DELETE-запроса для удаления каталога.
        """
        return super().delete(request, *args, **kwargs)

    def get_permissions(self):
        """
        Определяет права доступа для разных методов:
        - GET: доступ для всех пользователей.
        - PUT, PATCH, DELETE: доступ только для аутентифицированных владельцев и администраторов.
        """
        if self.request.method == "GET":
            return []  # Доступ для всех пользователей
        return [IsAuthenticated(), IsAdminOrBroker()]

    def perform_update(self, serializer):
        """
        Проверка прав доступа при обновлении каталога.
        """
        if (
            self.request.user != serializer.instance.broker
            and not self.request.user.is_superuser
        ):
            raise PermissionDenied("Вы можете изменять только свои каталоги.")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Проверка прав доступа при удалении каталога.
        """
        if self.request.user != instance.broker and not self.request.user.is_superuser:
            raise PermissionDenied("Вы можете удалять только свои каталоги.")
        instance.delete()
