import pytest
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_403_FORBIDDEN,
    HTTP_401_UNAUTHORIZED,
    HTTP_204_NO_CONTENT,
)
from django.urls import reverse
from properties.models import Catalog


@pytest.mark.django_db
class TestCatalogAPIPermissions:
    def test_admin_create_catalog(self, admin_user, api_client):
        """
        Администратор может создать каталог.
        """
        api_client.force_authenticate(admin_user)
        url = reverse("catalog-list")
        data = {
            "name": "Admin Catalog",
            "description": "Created by admin",
            "is_public": True,
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == HTTP_201_CREATED

    def test_broker_create_catalog(self, broker, api_client):
        """
        Брокер может создать каталог.
        """
        api_client.force_authenticate(broker)
        url = reverse("catalog-list")
        data = {
            "name": "Broker Catalog",
            "description": "Created by broker",
            "is_public": False,
        }

        response = api_client.post(url, data, format="json")
        assert response.status_code == HTTP_201_CREATED

    def test_buyer_cannot_create_catalog(self, buyer, api_client):
        """
        Покупатель не может создать каталог.
        """
        api_client.force_authenticate(buyer)
        url = reverse("catalog-list")
        data = {"name": "Invalid Catalog", "description": "Not allowed"}

        response = api_client.post(url, data, format="json")
        assert response.status_code == HTTP_403_FORBIDDEN

    def test_unauthorized_user_cannot_create_catalog(self, api_client):
        """
        Неавторизованный пользователь не может создать каталог.
        """
        url = reverse("catalog-list")
        data = {"name": "Unauthorized Catalog", "description": "No access"}

        response = api_client.post(url, data, format="json")
        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_get_public_catalogs(self, public_catalog, api_client):
        """
        Неавторизованный пользователь может получить публичные каталоги.
        """
        url = reverse("catalog-detail", args=[public_catalog.id])
        response = api_client.get(url)
        assert response.status_code == HTTP_200_OK

    def test_get_private_catalogs(self, private_catalog, broker, api_client):
        """
        Только владелец и администратор могут получить приватные каталоги.
        """
        # Владелец
        api_client.force_authenticate(broker)
        url = reverse("catalog-detail", args=[private_catalog.id])
        response = api_client.get(url)
        assert response.status_code == HTTP_200_OK

        # Неавторизованный пользователь
        api_client.logout()
        response = api_client.get(url)
        assert response.status_code == HTTP_403_FORBIDDEN

    def test_delete_catalog(self, broker, admin_user, catalog, api_client):
        """
        Владелец и администратор могут удалить каталог.
        """
        # Владелец удаляет каталог
        url = reverse("catalog-detail", args=[catalog.id])
        api_client.force_authenticate(broker)
        response = api_client.delete(url)
        assert response.status_code == HTTP_204_NO_CONTENT

        # Создаём новый каталог для администратора
        new_catalog = Catalog.objects.create(
            name="Admin Catalog", broker=admin_user, is_public=True
        )
        url = reverse("catalog-detail", args=[new_catalog.id])

        # Администратор удаляет каталог
        api_client.force_authenticate(admin_user)
        response = api_client.delete(url)
        assert response.status_code == HTTP_204_NO_CONTENT

    def test_unauthorized_cannot_delete_catalog(self, catalog, api_client):
        """
        Неавторизованный пользователь не может удалить каталог.
        """
        url = reverse("catalog-detail", args=[catalog.id])
        response = api_client.delete(url)
        assert response.status_code == HTTP_401_UNAUTHORIZED
