import pytest
from rest_framework.exceptions import ValidationError
from properties.serializers import ObjectSerializer, CatalogSerializer


@pytest.mark.django_db
class TestObjectSerializer:
    def test_valid_serialization(self, broker, mock_request):
        request = mock_request(broker)
        data = {
            "name": "Test Object",
            "price": 150000.00,
            "currency": "USD",
            "status": "sale",
            "country": "Country",
            "city": "City",
            "address": "Test Address",
            "area": 120.5,
            "rooms": 3,
            "broker": broker.id,
            "photos": ["http://example.com/photo1.jpg"],
            "videos": ["http://example.com/video1.mp4"],
            "features": {"key": "value"},
        }
        serializer = ObjectSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert instance.name == "Test Object"

    def test_duplicate_address_validation(self, real_estate_object, mock_request):
        request = mock_request(real_estate_object.broker)
        data = {
            "name": "Duplicate Object",
            "price": 120000,
            "country": real_estate_object.country,
            "city": real_estate_object.city,
            "address": real_estate_object.address,
            "area": 120,
            "rooms": 3,
            "broker": real_estate_object.broker.id,
            "photos": ["http://example.com/photo.jpg"],
            "videos": ["http://example.com/video.mp4"],
            "features": {"key": "value"},
        }
        serializer = ObjectSerializer(data=data, context={"request": request})
        with pytest.raises(ValidationError) as excinfo:
            serializer.is_valid(raise_exception=True)
        assert "Объект с таким адресом уже существует" in str(excinfo.value)

    def test_invalid_broker(self, broker, another_broker, mock_request):
        """
        Проверка, что broker автоматически привязывается при создании
        и не может быть изменён при обновлении.
        """
        request = mock_request(broker)

        # Тест создания объекта – broker должен быть установлен автоматически
        data = {
            "name": "Test Object",
            "price": 100000,
            "country": "Country",
            "city": "City",
            "address": "Test Address",
            "area": 100,
            "rooms": 3,
            "photos": ["http://example.com/photo1.jpg"],
            "videos": ["http://example.com/video1.mp4"],
            "features": {"key": "value"},
        }
        serializer = ObjectSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        instance = serializer.save()
        assert (
            instance.broker == broker
        )  # Проверяем, что broker – это текущий пользователь

        # Тест обновления объекта – попытка передать broker не должна его изменить
        update_data = {
            "broker": another_broker.id,  # Попытка изменить брокера
            "name": "Updated Test Object",
            "price": instance.price,  # Обязательное поле
            "country": instance.country,
            "city": instance.city,
            "address": instance.address,
            "area": instance.area,
            "rooms": instance.rooms,
        }
        serializer = ObjectSerializer(instance=instance, data=update_data, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated_instance = serializer.save()

        # Проверяем, что broker остался прежним
        assert updated_instance.broker == broker
        assert updated_instance.name == "Updated Test Object"


@pytest.mark.django_db
class TestCatalogSerializer:
    def test_valid_catalog_creation(self, broker, real_estate_object, mock_request):
        request = mock_request(broker)
        data = {
            "name": "Test Catalog",
            "description": "Catalog Description",
            "is_public": True,
            "catalog_objects": [real_estate_object.id],
        }

        # Создаем экземпляр сериализатора
        serializer = CatalogSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors

        # Передаем broker вручную, как это делает perform_create
        instance = serializer.save(broker=broker)

        # Проверки
        assert instance.name == "Test Catalog"
        assert instance.description == "Catalog Description"
        assert instance.is_public is True
        assert instance.broker == broker
        assert instance.listings.count() == 1
        assert instance.listings.first().listing == real_estate_object

    def test_update_catalog_objects(
        self, catalog, real_estate_object, another_real_estate_object, mock_request
    ):
        """
        Проверка обновления каталога и замены объектов недвижимости.
        """
        request = mock_request(catalog.broker)
        catalog.listings.create(listing=real_estate_object, sort_order=1)

        data = {
            "name": "Updated Catalog",
            "catalog_objects": [another_real_estate_object.id],
        }
        serializer = CatalogSerializer(
            instance=catalog, data=data, partial=True, context={"request": request}
        )
        assert serializer.is_valid(), serializer.errors
        updated_catalog = serializer.save()
        assert updated_catalog.name == "Updated Catalog"
        assert updated_catalog.listings.count() == 1
        assert updated_catalog.listings.first().listing == another_real_estate_object
