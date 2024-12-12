from rest_framework import serializers
from .models import (
    RealEstateObject,
    Catalog,
    CatalogListing,
)


class ObjectSerializer(serializers.ModelSerializer):
    photos = serializers.JSONField()
    videos = serializers.JSONField()
    features = serializers.JSONField()

    class Meta:
        model = RealEstateObject
        fields = "__all__"


class CatalogSerializer(serializers.ModelSerializer):
    catalog_objects = serializers.PrimaryKeyRelatedField(
        many=True, queryset=RealEstateObject.objects.all(), required=False
    )
    broker = serializers.ReadOnlyField(
        source="broker.email"
    )  # Добавляем поле только для чтения

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
        # Извлекаем данные связанных объектов
        objects_data = validated_data.pop("catalog_objects", [])
        catalog = Catalog.objects.create(**validated_data)  # Создаем каталог
        for obj in objects_data:
            CatalogListing.objects.create(catalog=catalog, listing=obj)
        return catalog

    def update(self, instance, validated_data):
        # Извлекаем данные связанных объектов
        objects_data = validated_data.pop("catalog_objects", None)
        # Обновляем остальные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        # Обновляем связь с объектами, если они переданы
        if objects_data is not None:
            instance.listings.set(objects_data)
        instance.save()
        return instance
