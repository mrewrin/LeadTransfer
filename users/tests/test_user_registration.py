import pytest
from rest_framework.reverse import reverse
from rest_framework import status
from users.models import User


@pytest.mark.django_db
def test_user_registration(api_client, create_roles):
    """Тест регистрации нового пользователя с базовой ролью."""
    url = reverse("register")  # Убедитесь, что это имя эндпоинта регистрации
    payload = {
        "email": "testuser@example.com",
        "password": "Test123!",
        "role": "buyer",
    }

    response = api_client.post(url, payload)

    # Проверяем, что запрос успешен
    assert response.status_code == status.HTTP_201_CREATED
    assert User.objects.filter(email=payload["email"]).exists()

    # Проверяем, что созданный пользователь имеет правильную роль
    user = User.objects.get(email=payload["email"])
    assert user.profile.role.name == "buyer"


@pytest.mark.django_db
def test_registration_without_role(api_client, create_roles):
    """Тест регистрации пользователя без указания роли."""
    url = reverse("register")
    payload = {
        "email": "testuser2@example.com",
        "password": "Test123!",
    }

    response = api_client.post(url, payload)

    # Проверяем, что запрос отклонен
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "role" in response.data


@pytest.mark.django_db
def test_duplicate_user_registration(api_client, create_roles):
    """Тест регистрации пользователя с существующим email."""
    url = reverse("register")
    payload = {
        "email": "testuser@example.com",
        "password": "Test123!",
        "role": "buyer",
    }

    # Первая регистрация
    response = api_client.post(url, payload)
    assert response.status_code == status.HTTP_201_CREATED

    # Попытка зарегистрировать того же пользователя
    response = api_client.post(url, payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


@pytest.mark.django_db
def test_admin_role_registration(api_client, create_roles):
    """Тест регистрации пользователя с ролью администратора."""
    url = reverse("register")
    payload = {
        "email": "adminuser@example.com",
        "password": "Admin123!",
        "role": "admin",
    }

    response = api_client.post(url, payload)

    # Проверяем, что запрос успешен
    assert response.status_code == status.HTTP_201_CREATED
    user = User.objects.get(email=payload["email"])
    assert user.profile.role.name == "admin"


@pytest.mark.django_db
def test_invalid_role_registration(api_client, create_roles):
    """Тест регистрации с недопустимой ролью."""
    url = reverse("register")
    payload = {
        "email": "invalidroleuser@example.com",
        "password": "Test123!",
        "role": "invalid_role",
    }

    response = api_client.post(url, payload)

    # Проверяем, что запрос отклонен
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "role" in response.data
