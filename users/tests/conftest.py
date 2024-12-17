import pytest
from rest_framework.test import APIClient, APIRequestFactory
from users.models import Role, User, UserProfile


@pytest.fixture
def api_client():
    """Возвращает клиент для API."""
    return APIClient()


@pytest.fixture
def create_roles(db):
    """Создает базовые роли для пользователей."""
    roles = ["buyer", "broker", "admin", "moderator", "ambassador"]
    for role in roles:
        Role.objects.get_or_create(name=role)


@pytest.fixture
def admin_user(db, create_roles):
    """Создает администратора с ролью 'admin'."""
    role = Role.objects.get(name="admin")
    user = User.objects.create_user(
        email="admin@example.com",
        password="Admin123!",
        is_staff=True,
        is_active=True,
    )
    # Явно создаем профиль пользователя
    UserProfile.objects.create(user=user, role=role)
    return user


@pytest.fixture
def broker_user(db, create_roles):
    """Создает брокера с ролью 'broker'."""
    role = Role.objects.get(name="broker")
    user = User.objects.create_user(
        email="broker@example.com",
        password="Broker123!",
        is_active=True,
    )
    # Явно создаем профиль пользователя
    UserProfile.objects.create(user=user, role=role)
    return user


@pytest.fixture
def buyer_user(db, create_roles):
    """Создает покупателя с ролью 'buyer'."""
    role = Role.objects.get(name="buyer")
    user = User.objects.create_user(
        email="buyer@example.com",
        password="Buyer123!",
        is_active=True,
    )
    # Явно создаем профиль пользователя
    UserProfile.objects.create(user=user, role=role)
    return user


@pytest.fixture
def moderator_user(db, create_roles):
    """Создает модератора с ролью 'moderator'."""
    role = Role.objects.get(name="moderator")
    user = User.objects.create_user(
        email="moderator@example.com",
        password="Moderator123!",
        is_staff=True,
        is_active=True,
    )
    # Явно создаем профиль пользователя
    UserProfile.objects.create(user=user, role=role)
    return user


@pytest.fixture
def ambassador_user(db, create_roles):
    """Создает амбассадора с ролью 'ambassador'."""
    role = Role.objects.get(name="ambassador")
    user = User.objects.create_user(
        email="ambassador@example.com",
        password="Ambassador123!",
        is_active=True,
    )
    # Явно создаем профиль пользователя
    UserProfile.objects.create(user=user, role=role)
    return user


@pytest.fixture
def authenticated_client(api_client, admin_user):
    """Возвращает API клиент с авторизацией администратора."""
    response = api_client.post(
        "/api/auth/login/",
        {"email": admin_user.email, "password": "Admin123!"},
    )
    assert response.status_code == 200  # Убедитесь, что токен возвращается успешно
    token = response.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client


@pytest.fixture
def create_user_with_role():
    """
    Фикстура для создания пользователя с заданной ролью.
    """

    def _create_user(email, role_name):
        user = User.objects.create_user(email=email, password="password123")
        role, _ = Role.objects.get_or_create(name=role_name)
        UserProfile.objects.create(user=user, role=role)
        return user

    return _create_user


@pytest.fixture
def request_factory():
    """Фикстура для фабрики запросов."""
    return APIRequestFactory()
