import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_403_FORBIDDEN,
    HTTP_401_UNAUTHORIZED,
)


@pytest.mark.django_db
class TestCatalogPermissions:
    def test_admin_full_access(self, admin_user, api_client):
        """
        Администратор имеет полный доступ к каталогам.
        """
        api_client.force_authenticate(admin_user)
        url = reverse("catalog-list")

        # POST - создание каталога (без передачи broker)
        data = {
            "name": "Admin Catalog",
            "description": "Admin created this catalog",
            "is_public": True,
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 201, response.data

        catalog_id = response.data["id"]

        # PUT - обновление каталога
        url = reverse("catalog-detail", args=[catalog_id])
        update_data = {"name": "Updated Admin Catalog", "is_public": False}
        response = api_client.put(url, update_data, format="json")
        assert response.status_code == 200

        # DELETE - удаление каталога
        response = api_client.delete(url)
        assert response.status_code == 204

    def test_broker_manage_own_catalogs(self, broker, api_client):
        """
        Брокер может управлять только своими каталогами.
        """
        api_client.force_authenticate(broker)
        url = reverse("catalog-list")

        # Создание своего каталога (без передачи broker)
        data = {
            "name": "Broker Catalog",
            "description": "Catalog by broker",
            "is_public": True,
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 201, response.data
        catalog_id = response.data["id"]

        # Попытка обновить свой каталог
        url = reverse("catalog-detail", args=[catalog_id])
        update_data = {"name": "Updated Broker Catalog", "is_public": False}
        response = api_client.put(url, update_data, format="json")
        assert response.status_code == 200

    def test_buyer_read_only_access(self, buyer, catalog, api_client):
        """
        Покупатель имеет доступ только на чтение каталогов.
        """
        api_client.force_authenticate(buyer)
        url = reverse("catalog-detail", args=[catalog.id])

        # GET - просмотр каталога
        response = api_client.get(url)
        assert response.status_code == HTTP_200_OK

        # POST - попытка создания (должна быть запрещена)
        url = reverse("catalog-list")
        data = {"name": "Unauthorized Catalog", "is_public": True}
        response = api_client.post(url, data, format="json")
        assert response.status_code == HTTP_403_FORBIDDEN

    def test_unauthorized_user_read_only(self, public_catalog, api_client):
        """
        Неавторизованный пользователь имеет доступ только к публичным каталогам.
        """

        url = reverse("catalog-detail", args=[public_catalog.id])

        # GET - просмотр публичного каталога
        response = api_client.get(url)
        assert response.status_code == HTTP_200_OK

        # POST - попытка создания (должна быть запрещена)
        url = reverse("catalog-list")
        data = {"name": "Unauthorized Catalog", "is_public": True}
        response = api_client.post(url, data, format="json")
        assert response.status_code == HTTP_401_UNAUTHORIZED
