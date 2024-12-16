import pytest
from unittest.mock import Mock
from properties.models import RealEstateObject, Catalog, CatalogListing
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def broker():
    """
    Фикстура для создания пользователя с ролью брокера.
    """
    return User.objects.create_user(email="broker@test.com", password="password123")


@pytest.fixture
def another_broker():
    """
    Фикстура для создания другого пользователя с ролью брокера.
    """
    return User.objects.create_user(
        email="another_broker@test.com", password="password123"
    )


@pytest.fixture
def mock_request():
    """
    Фикстура для мока запроса с пользователем.
    """

    def _mock_request(user):
        request = Mock()
        request.user = user
        return request

    return _mock_request


@pytest.fixture
def real_estate_object(broker):
    """
    Фикстура для создания объекта недвижимости.
    """
    return RealEstateObject.objects.create(
        name="Test Property",
        price=150000.00,
        currency="USD",
        status="sale",
        country="Country",
        city="City",
        address="123 Main Street",
        area=120.5,
        rooms=3,
        broker=broker,
    )


@pytest.fixture
def another_real_estate_object(broker):
    """
    Фикстура для создания второго объекта недвижимости.
    """
    return RealEstateObject.objects.create(
        name="Another Property",
        price=120000.00,
        currency="USD",
        status="rent",
        country="Country",
        city="City",
        address="456 Elm Street",
        area=130.0,
        rooms=4,
        broker=broker,
    )


@pytest.fixture
def real_estate_objects(broker):
    """
    Фикстура для создания нескольких объектов недвижимости.
    """
    return [
        RealEstateObject.objects.create(
            name="Object 1",
            price=100000.00,
            currency="USD",
            status="sale",
            country="Country",
            city="City",
            address="123 Main Street",
            area=120.5,
            rooms=3,
            broker=broker,
        ),
        RealEstateObject.objects.create(
            name="Object 2",
            price=150000.00,
            currency="USD",
            status="rent",
            country="Country",
            city="City",
            address="456 Elm Street",
            area=130.0,
            rooms=4,
            broker=broker,
        ),
    ]


@pytest.fixture
def catalog(broker):
    """
    Фикстура для создания каталога.
    """
    return Catalog.objects.create(
        name="Test Catalog",
        description="Sample Description",
        is_public=True,
        broker=broker,
    )


@pytest.fixture
def catalog_with_listings(catalog, real_estate_objects):
    """
    Фикстура для создания каталога с объектами недвижимости.
    """
    for idx, obj in enumerate(real_estate_objects):
        CatalogListing.objects.create(catalog=catalog, listing=obj, sort_order=idx + 1)
    return catalog


@pytest.fixture
def catalog_listing(catalog, real_estate_object):
    """
    Фикстура для создания записи в CatalogListing.
    """
    return CatalogListing.objects.create(catalog=catalog, listing=real_estate_object)
