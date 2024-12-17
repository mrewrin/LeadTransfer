import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from unittest.mock import Mock
from properties.models import RealEstateObject, Catalog, CatalogListing
from users.models import UserProfile, Role

User = get_user_model()


@pytest.fixture
def api_client():
    """
    Фикстура для создания API клиента.
    """
    return APIClient()


@pytest.fixture
def admin_user():
    """
    Фикстура для создания пользователя с правами администратора.
    """
    return User.objects.create_superuser(email="admin@test.com", password="password123")


@pytest.fixture
def buyer():
    """
    Фикстура для создания пользователя с ролью покупателя.
    """
    user = User.objects.create_user(email="buyer@test.com", password="password123")
    UserProfile.objects.create(
        user=user, role=Role.objects.get_or_create(name="buyer")[0]
    )
    return user


@pytest.fixture
def broker():
    """
    Фикстура для создания пользователя с ролью брокера.
    """
    user = User.objects.create_user(email="broker@test.com", password="password123")
    role, _ = Role.objects.get_or_create(name="broker")  # Создаем роль, если её еще нет
    UserProfile.objects.create(user=user, role=role)  # Привязываем роль к пользователю
    return user


@pytest.fixture
def another_broker():
    """
    Фикстура для создания другого пользователя с ролью брокера.
    """
    user = User.objects.create_user(
        email="another_broker@test.com", password="password123"
    )
    role, _ = Role.objects.get_or_create(name="broker")  # Создаем роль, если её еще нет
    UserProfile.objects.create(user=user, role=role)  # Привязываем роль к пользователю
    return user


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
        name="Test Catalog", description="Public catalog", is_public=True, broker=broker
    )


@pytest.fixture
def public_catalog(broker):
    return Catalog.objects.create(
        name="Public Catalog",
        description="This catalog is public",
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


@pytest.fixture
def private_catalog(broker):
    """
    Фикстура для создания приватного каталога.
    """
    return Catalog.objects.create(
        name="Private Catalog",
        description="This catalog is private",
        is_public=False,
        broker=broker,
    )


@pytest.fixture
def another_broker_catalog(another_broker):
    """
    Фикстура для создания каталога другого брокера.
    """
    return Catalog.objects.create(
        name="Another Broker's Catalog",
        description="Catalog owned by another broker",
        is_public=True,
        broker=another_broker,
    )
