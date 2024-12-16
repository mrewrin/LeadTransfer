from rest_framework import serializers
from .models import (
    RealEstateObject,
    Catalog,
    CatalogListing,
)


class ObjectSerializer(serializers.ModelSerializer):
    """
    Сериализатор для объектов недвижимости.

    Поля:
        - photos: JSON-поле для хранения фотографий объекта.
        - videos: JSON-поле для хранения видео объекта.
        - features: JSON-поле для хранения характеристик объекта.
    """

    photos = serializers.JSONField()
    videos = serializers.JSONField()
    features = serializers.JSONField()

    class Meta:
        model = RealEstateObject
        fields = "__all__"

    def validate(self, attrs):
        request = self.context.get("request")
        if (
            request
            and not request.user.is_superuser
            and attrs.get("broker") != request.user
        ):
            raise serializers.ValidationError(
                "Вы можете управлять только своими объектами."
            )
        return super().validate(attrs)


class CatalogSerializer(serializers.ModelSerializer):
    """
    Сериализатор для каталогов.

    Поля:
        - id: ID каталога.
        - name: Название каталога.
        - description: Описание каталога.
        - is_public: Флаг публичности каталога.
        - broker: Email брокера (только для чтения).
        - tags: Теги каталога.
        - catalog_objects: Список объектов недвижимости, связанных с каталогом.
    """

    catalog_objects = serializers.PrimaryKeyRelatedField(
        many=True, queryset=RealEstateObject.objects.all(), required=False
    )
    broker = serializers.ReadOnlyField(source="broker.email")

    class Meta:
        model = Catalog
        fields = [
            "id",
            "name",
            "description",
            "is_public",
            "broker",
            "tags",
            "catalog_objects",
        ]
        read_only_fields = ["broker"]

    def create(self, validated_data):
        """
        Создает новый каталог и связывает его с указанными объектами недвижимости.

        Args:
            validated_data (dict): Валидированные данные для создания каталога.

        Returns:
            Catalog: Созданный экземпляр каталога.
        """
        objects_data = validated_data.pop("catalog_objects", [])
        catalog = Catalog.objects.create(**validated_data)
        for obj in objects_data:
            CatalogListing.objects.create(catalog=catalog, listing=obj)
        return catalog

    def update(self, instance, validated_data):
        """
        Обновляет существующий каталог и обновляет связь с объектами недвижимости.

        Args:
            instance (Catalog): Существующий экземпляр каталога.
            validated_data (dict): Валидированные данные для обновления.

        Returns:
            Catalog: Обновленный экземпляр каталога.
        """
        objects_data = validated_data.pop("catalog_objects", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if objects_data is not None:
            instance.listings.set(objects_data)
        instance.save()
        return instance
