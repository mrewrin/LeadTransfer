from django.core.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
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
        return [IsAuthenticatedOrReadOnly()]


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
        return [IsAuthenticatedOrReadOnly()]


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
        serializer.save(broker=self.request.user)

    def get_permissions(self):
        if self.request.method in ["POST"]:
            return [IsAdminOrBroker()]
        return [IsAuthenticatedOrReadOnly()]


class CatalogDetailView(RetrieveUpdateDestroyAPIView):
    """
    API представление для детального просмотра, обновления и удаления каталога.
    """

    queryset = Catalog.objects.all()
    serializer_class = CatalogSerializer

    @swagger_auto_schema(
        operation_summary="Получить детали каталога",
        operation_description="Возвращает подробную информацию о каталоге.",
        responses={200: CatalogSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновить каталог",
        operation_description="Обновляет данные каталога. "
        "Доступно только владельцу каталога или администратору.",
        request_body=CatalogSerializer,
        responses={200: CatalogSerializer, 403: "Доступ запрещен"},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удалить каталог",
        operation_description="Удаляет каталог. "
        "Доступно только владельцу каталога или администратору.",
        responses={204: "Каталог успешно удален", 403: "Доступ запрещен"},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_update(self, serializer):
        if (
            self.request.user != serializer.instance.broker
            and not self.request.user.is_superuser
        ):
            raise PermissionDenied("Вы можете изменять только свои каталоги.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user != instance.broker and not self.request.user.is_superuser:
            raise PermissionDenied("Вы можете удалять только свои каталоги.")
        instance.delete()

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminOrBroker()]
        return [IsAuthenticatedOrReadOnly()]
