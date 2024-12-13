from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from .models import Catalog, RealEstateObject
from .serializers import ObjectSerializer, CatalogSerializer


class ObjectListCreateView(ListCreateAPIView):
    """
    API представление для получения списка объектов недвижимости и их создания.

    Методы:
        - GET: Возвращает список объектов недвижимости с возможностью фильтрации.
        - POST: Создает новый объект недвижимости.

    Фильтры:
        - price_min: Минимальная цена.
        - price_max: Максимальная цена.
        - status: Статус объекта.
        - country: Страна.
    """

    queryset = RealEstateObject.objects.all()
    serializer_class = ObjectSerializer

    def get_queryset(self):
        """
        Получает QuerySet объектов недвижимости с учетом фильтров из параметров запроса.

        Returns:
            QuerySet: Отфильтрованный QuerySet объектов недвижимости.
        """
        queryset = super().get_queryset()
        price_min = self.request.query_params.get("price_min")
        price_max = self.request.query_params.get("price_max")
        status = self.request.query_params.get("status")
        country = self.request.query_params.get("country")

        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)
        if status:
            queryset = queryset.filter(status=status)
        if country:
            queryset = queryset.filter(country__icontains=country)

        return queryset


class ObjectDetailView(RetrieveUpdateDestroyAPIView):
    """
    API представление для детального просмотра, обновления и удаления объекта недвижимости.

    Методы:
        - GET: Возвращает детальную информацию об объекте.
        - PUT/PATCH: Обновляет информацию об объекте.
        - DELETE: Удаляет объект.
    """

    queryset = RealEstateObject.objects.all()
    serializer_class = ObjectSerializer


class CatalogListCreateView(ListCreateAPIView):
    """
    API представление для получения списка каталогов и их создания.

    Методы:
        - GET: Возвращает список каталогов с возможностью фильтрации.
        - POST: Создает новый каталог.

    Фильтры:
        - owner: ID владельца каталога.
    """

    queryset = Catalog.objects.all()
    serializer_class = CatalogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Получает QuerySet каталогов с учетом фильтров из параметров запроса.

        Returns:
            QuerySet: Отфильтрованный QuerySet каталогов.
        """
        queryset = Catalog.objects.all()
        owner = self.request.query_params.get("owner")
        if owner:
            queryset = queryset.filter(broker_id=int(owner))
        return queryset

    def post(self, request, *args, **kwargs):
        """
        Создает новый каталог, привязывая его к текущему пользователю.

        Args:
            request: Объект HTTP-запроса.

        Returns:
            Response: Ответ с данными нового каталога или ошибкой.
        """
        print(f"DEBUG: request.user = {request.user}, type = {type(request.user)}")

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(broker=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CatalogDetailView(RetrieveUpdateDestroyAPIView):
    """
    API представление для детального просмотра, обновления и удаления каталога.

    Методы:
        - GET: Возвращает детальную информацию о каталоге.
        - PUT/PATCH: Обновляет информацию о каталоге.
        - DELETE: Удаляет каталог.
    """

    queryset = Catalog.objects.all()
    serializer_class = CatalogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def put(self, request, *args, **kwargs):
        """
        Обновляет информацию о каталоге.

        Args:
            request: Объект HTTP-запроса.

        Returns:
            Response: Ответ с обновленными данными каталога или ошибкой.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
