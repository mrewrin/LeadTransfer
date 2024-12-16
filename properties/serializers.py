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
        - photos: JSON-поле для хранения ссылок на фотографии объекта.
        - videos: JSON-поле для хранения ссылок на видео объекта.
        - features: JSON-поле для хранения дополнительных характеристик объекта.
    """

    photos = serializers.JSONField(help_text="Список ссылок на фотографии объекта.")
    videos = serializers.JSONField(help_text="Список ссылок на видео объекта.")
    features = serializers.JSONField(help_text="Дополнительные характеристики объекта.")

    class Meta:
        model = RealEstateObject
        fields = "__all__"

    def validate(self, attrs):
        """
        Валидация данных объекта недвижимости.

        Проверяет:
            - Право управления объектом (только для брокера).
            - Уникальность адреса, если поле `complex_name` не указано.

        Args:
            attrs (dict): Входные данные для валидации.

        Returns:
            dict: Валидированные данные.

        Raises:
            serializers.ValidationError: В случае нарушения условий валидации.
        """
        request = self.context.get("request")
        if (
            request
            and not request.user.is_superuser
            and attrs.get("broker") != request.user
        ):
            raise serializers.ValidationError(
                "Вы можете управлять только своими объектами."
            )

        # Проверка уникальности адреса
        if not attrs.get("complex_name"):
            duplicates = RealEstateObject.objects.filter(
                country=attrs["country"],
                city=attrs["city"],
                district=attrs.get("district"),
                address=attrs["address"],
            )
            if self.instance:
                duplicates = duplicates.exclude(id=self.instance.id)
            if duplicates.exists():
                raise serializers.ValidationError(
                    "Объект с таким адресом уже существует."
                )

        if attrs.get("price") is None:
            raise serializers.ValidationError(
                {"price": "Цена обязательна для заполнения."}
            )
        return super().validate(attrs)


class CatalogSerializer(serializers.ModelSerializer):
    """
    Сериализатор для каталогов объектов недвижимости.

    Поля:
        - id: Уникальный идентификатор каталога.
        - name: Название каталога.
        - description: Описание каталога.
        - is_public: Флаг публичности каталога (True/False).
        - broker: Email брокера, который владеет каталогом (только для чтения).
        - tags: Теги каталога (опциональные).
        - catalog_objects: Список ID объектов недвижимости, связанных с каталогом.
    """

    catalog_objects = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=RealEstateObject.objects.all(),
        required=False,
        help_text="Список ID объектов недвижимости, связанных с каталогом.",
    )
    broker = serializers.ReadOnlyField(
        source="broker.email", help_text="Email брокера."
    )

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
        Создает новый каталог и связывает его с объектами недвижимости.

        Args:
            validated_data (dict): Валидированные данные.

        Returns:
            Catalog: Созданный экземпляр каталога.
        """
        objects_data = validated_data.pop("catalog_objects", [])
        request = self.context.get("request")
        broker = request.user if request else None
        catalog = Catalog.objects.create(broker=broker, **validated_data)
        for obj in objects_data:
            CatalogListing.objects.create(catalog=catalog, listing=obj)
        return catalog

    def update(self, instance, validated_data):
        """
        Обновляет существующий каталог и обновляет связь с объектами недвижимости.

        Args:
            instance (Catalog): Экземпляр каталога для обновления.
            validated_data (dict): Валидированные данные.

        Returns:
            Catalog: Обновленный экземпляр каталога.
        """
        objects_data = validated_data.pop("catalog_objects", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if objects_data is not None:
            # Удаляем старые связи
            instance.listings.all().delete()
            # Убедимся, что передаются только ID
            objects_data = [
                obj.id if isinstance(obj, RealEstateObject) else obj
                for obj in objects_data
            ]
            for obj_id in objects_data:
                instance.listings.create(listing_id=obj_id)
        instance.save()
        return instance
