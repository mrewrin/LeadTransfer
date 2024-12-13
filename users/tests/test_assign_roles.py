import pytest
from rest_framework.reverse import reverse
from rest_framework import status

# from users.models import User


@pytest.mark.django_db
def test_admin_can_assign_role(authenticated_client, buyer_user, create_roles):
    """Тест, что администратор может назначить роль пользователю."""
    url = reverse("assign_role")  # Убедитесь, что это имя эндпоинта назначения ролей
    payload = {
        "user_id": buyer_user.id,
        "role": "broker",
    }

    response = authenticated_client.post(url, payload)

    # Проверяем, что запрос успешен
    assert response.status_code == status.HTTP_200_OK

    # Проверяем, что роль пользователя обновлена
    buyer_user.refresh_from_db()
    assert buyer_user.profile.role.name == "broker"


@pytest.mark.django_db
def test_assign_role_with_invalid_user(authenticated_client, create_roles):
    """Тест назначения роли несуществующему пользователю."""
    url = reverse("assign_role")
    payload = {
        "user_id": 9999,  # Несуществующий ID
        "role": "broker",
    }

    response = authenticated_client.post(url, payload)

    # Проверяем, что запрос отклонен
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "UserProfile not found" in response.data["error"]
