from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from .models import Catalog, RealEstateObject
from .serializers import ObjectSerializer, CatalogSerializer


class ObjectListCreateView(ListCreateAPIView):
    queryset = RealEstateObject.objects.all()
    serializer_class = ObjectSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтрация по параметрам запроса
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
    queryset = RealEstateObject.objects.all()
    serializer_class = ObjectSerializer


# Список и создание каталогов
class CatalogListCreateView(ListCreateAPIView):
    queryset = Catalog.objects.all()
    serializer_class = CatalogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Catalog.objects.all()
        # Добавьте фильтры по необходимости, например, по пользователю или тегам
        owner = self.request.query_params.get("owner")
        if owner:
            queryset = queryset.filter(broker_id=int(owner))
        return queryset

    def post(self, request, *args, **kwargs):
        print(f"DEBUG: request.user = {request.user}, type = {type(request.user)}")

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                broker=self.request.user
            )  # Привязываем каталог к текущему пользователю
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Детальный просмотр, обновление, удаление
class CatalogDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Catalog.objects.all()
    serializer_class = CatalogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
