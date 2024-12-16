import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from properties.models import (
    RealEstateObject,
)

User = get_user_model()


@pytest.mark.django_db
class TestRealEstateObject:
    def test_create_real_estate_object(self, real_estate_object):
        """
        Проверка создания объекта недвижимости с фикстурой.
        """
        assert real_estate_object.id is not None
        assert real_estate_object.name == "Test Property"
        assert real_estate_object.price == 150000.00

    def test_validate_unique_address(self, real_estate_object, broker):
        """
        Проверка валидации на дублирование адреса (при пустом complex_name).
        """
        duplicate_obj = RealEstateObject(
            name="Duplicate Object",
            price=120000.00,
            country=real_estate_object.country,
            city=real_estate_object.city,
            address=real_estate_object.address,
            area=150.0,
            rooms=4,
            broker=broker,
        )
        with pytest.raises(ValidationError):
            duplicate_obj.clean()

    def test_required_fields(self, broker):
        """
        Проверка ошибки при отсутствии обязательных полей.
        """
        with pytest.raises(IntegrityError):
            RealEstateObject.objects.create(
                country="Country",
                city="City",
                broker=broker,
            )


@pytest.mark.django_db
class TestCatalog:
    def test_create_catalog(self, catalog):
        """
        Проверка создания каталога с фикстурой.
        """
        assert catalog.id is not None
        assert catalog.name == "Test Catalog"
        assert catalog.is_public is True

    def test_catalog_with_listings(self, catalog_with_listings):
        """
        Проверка добавления объектов недвижимости в каталог.
        """
        assert catalog_with_listings.listings.count() == 2
        assert catalog_with_listings.listings.first().listing.name == "Object 1"
        assert catalog_with_listings.listings.last().listing.name == "Object 2"
