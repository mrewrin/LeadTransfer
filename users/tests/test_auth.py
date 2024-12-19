import pytest
import time
from datetime import timedelta
from rest_framework.reverse import reverse
from rest_framework import status
from users.models import User, Role, UserProfile


@pytest.mark.django_db
def test_login_with_valid_credentials(api_client, admin_user):
    """Тест успешной авторизации с корректными данными."""
    url = reverse("token_obtain_pair")
    payload = {
        "email": "admin@example.com",
        "password": "Admin123!",
    }

    response = api_client.post(url, payload)

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_login_with_invalid_credentials(api_client):
    """Тест авторизации с некорректными данными."""
    url = reverse("token_obtain_pair")
    payload = {
        "email": "wrong@example.com",
        "password": "Wrong123!",
    }

    response = api_client.post(url, payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "No active account" in response.data["detail"]


@pytest.mark.django_db
def test_login_with_inactive_user(api_client, create_roles):
    """Тест авторизации с неактивным пользователем."""
    # Создаем неактивного пользователя и его профиль
    role = Role.objects.get(name="buyer")
    user = User.objects.create_user(
        email="inactive@example.com", password="Inactive123!", is_active=False
    )
    UserProfile.objects.create(user=user, role=role)

    url = reverse("token_obtain_pair")
    payload = {
        "email": "inactive@example.com",
        "password": "Inactive123!",
    }

    response = api_client.post(url, payload)

    # Проверяем, что запрос отклонен
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "No active account" in response.data["detail"]


@pytest.mark.django_db
def test_login_with_wrong_password(api_client, admin_user):
    """Тест авторизации с неправильным паролем."""
    url = reverse("token_obtain_pair")
    payload = {
        "email": "admin@example.com",
        "password": "WrongPassword!",
    }

    response = api_client.post(url, payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "No active account" in response.data["detail"]


@pytest.mark.django_db
def test_refresh_token(api_client, admin_user):
    """Тест обновления токена с использованием refresh-токена."""
    # Получаем токены
    login_url = reverse("token_obtain_pair")
    payload = {
        "email": "admin@example.com",
        "password": "Admin123!",
    }
    response = api_client.post(login_url, payload)
    refresh_token = response.data["refresh"]

    # Обновляем access-токен
    refresh_url = reverse("token_refresh")
    refresh_payload = {"refresh": refresh_token}

    response = api_client.post(refresh_url, refresh_payload)

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data


@pytest.mark.django_db
def test_login_with_missing_fields(api_client):
    """Тест авторизации с отсутствующими данными."""
    url = reverse("token_obtain_pair")
    payload = {"email": "admin@example.com"}  # Без пароля

    response = api_client.post(url, payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.data

    payload = {"password": "Admin123!"}  # Без email
    response = api_client.post(url, payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "email" in response.data


@pytest.mark.django_db
def test_expired_access_token(api_client, admin_user, settings):
    """Тест авторизации с истекшим токеном."""
    settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(seconds=1)

    login_url = reverse("token_obtain_pair")
    payload = {
        "email": "admin@example.com",
        "password": "Admin123!",
    }
    response = api_client.post(login_url, payload)
    access_token = response.data["access"]

    time.sleep(3)

    # Попробуем получить защищенный ресурс
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    protected_url = reverse("protected")
    response = api_client.get(protected_url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.data, f"Response data: {response.data}"
    # assert "token_not_valid" in response.data["detail"]


@pytest.mark.django_db
def test_change_password_with_valid_data(api_client, admin_user):
    """
    Тест успешной смены пароля с корректными данными.
    """
    login_url = reverse("token_obtain_pair")
    change_password_url = reverse("change_password")

    # Авторизация
    payload = {"email": "admin@example.com", "password": "Admin123!"}
    response = api_client.post(login_url, payload)
    access_token = response.data["access"]

    # Смена пароля
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    response = api_client.post(
        change_password_url,
        {"old_password": "Admin123!", "new_password": "NewPassword123!"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert "Password changed successfully!" in response.data["message"]

    # Проверяем, что старый пароль больше не работает
    response = api_client.post(login_url, payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Новый пароль работает
    response = api_client.post(
        login_url, {"email": "admin@example.com", "password": "NewPassword123!"}
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_change_password_with_invalid_old_password(api_client, admin_user):
    """
    Тест смены пароля с неправильным старым паролем.
    """
    login_url = reverse("token_obtain_pair")
    change_password_url = reverse("change_password")

    # Авторизация
    payload = {"email": "admin@example.com", "password": "Admin123!"}
    response = api_client.post(login_url, payload)
    access_token = response.data["access"]

    # Смена пароля
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    response = api_client.post(
        change_password_url,
        {"old_password": "WrongOldPassword!", "new_password": "NewPassword123!"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "The old password is incorrect." in response.data["error"]
