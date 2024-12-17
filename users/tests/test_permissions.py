import pytest
from rest_framework.reverse import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from users.permissions import (
    IsAdminOrModerator,
    IsBrokerOrAmbassador,
    IsAdminOrBroker,
    IsBuyer,
)

User = get_user_model()


@pytest.mark.django_db
def test_admin_access_to_admin_view(authenticated_client):
    """Тест доступа администратора к защищенному эндпоинту."""
    url = reverse("admin-or-moderator")
    response = authenticated_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Welcome, Admin or Moderator!"


@pytest.mark.django_db
class TestCustomPermissions:
    def test_is_admin_or_moderator(self, create_user_with_role, request_factory):
        """
        Проверка разрешения IsAdminOrModerator.
        """
        permission = IsAdminOrModerator()

        # Создаем пользователя с ролью "admin"
        admin_user = create_user_with_role("admin@test.com", "admin")
        request = request_factory.get("/")
        request.user = admin_user
        assert permission.has_permission(request, None) is True

        # Создаем пользователя с ролью "moderator"
        moderator_user = create_user_with_role("moderator@test.com", "moderator")
        request.user = moderator_user
        assert permission.has_permission(request, None) is True

        # Проверка для пользователя с ролью "broker"
        broker_user = create_user_with_role("broker@test.com", "broker")
        request.user = broker_user
        assert permission.has_permission(request, None) is False

    def test_is_broker_or_ambassador(self, create_user_with_role, request_factory):
        """
        Проверка разрешения IsBrokerOrAmbassador.
        """
        permission = IsBrokerOrAmbassador()

        # Создаем пользователя с ролью "broker"
        broker_user = create_user_with_role("broker@test.com", "broker")
        request = request_factory.get("/")
        request.user = broker_user
        assert permission.has_permission(request, None) is True

        # Создаем пользователя с ролью "ambassador"
        ambassador_user = create_user_with_role("ambassador@test.com", "ambassador")
        request.user = ambassador_user
        assert permission.has_permission(request, None) is True

        # Проверка для пользователя с ролью "buyer"
        buyer_user = create_user_with_role("buyer@test.com", "buyer")
        request.user = buyer_user
        assert permission.has_permission(request, None) is False

    def test_is_admin_or_broker(self, create_user_with_role, request_factory):
        """
        Проверка разрешения IsAdminOrBroker.
        """
        permission = IsAdminOrBroker()

        # Создаем пользователя с ролью "broker"
        broker_user = create_user_with_role("broker@test.com", "broker")
        request = request_factory.get("/")
        request.user = broker_user
        assert permission.has_permission(request, None) is True

        # Создаем суперпользователя
        superuser = User.objects.create_superuser(
            email="superuser@test.com", password="password123"
        )
        request.user = superuser
        assert permission.has_permission(request, None) is True

        # Проверка для пользователя с ролью "buyer"
        buyer_user = create_user_with_role("buyer@test.com", "buyer")
        request.user = buyer_user
        assert permission.has_permission(request, None) is False

    def test_is_buyer(self, create_user_with_role, request_factory):
        """
        Проверка разрешения IsBuyer.
        """
        permission = IsBuyer()

        # Создаем пользователя с ролью "buyer"
        buyer_user = create_user_with_role("buyer@test.com", "buyer")
        request = request_factory.get("/")
        request.user = buyer_user
        assert permission.has_permission(request, None) is True

        # Проверка для пользователя с ролью "admin"
        admin_user = create_user_with_role("admin@test.com", "admin")
        request.user = admin_user
        assert permission.has_permission(request, None) is False
