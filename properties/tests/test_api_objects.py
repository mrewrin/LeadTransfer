import pytest
from django.urls import reverse
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_403_FORBIDDEN,
    HTTP_401_UNAUTHORIZED,
    HTTP_204_NO_CONTENT,
)


@pytest.mark.django_db
class TestRealEstateObjectAPI:
    def test_admin_can_create_object(self, admin_user, api_client):
        """
        Администратор может создать объект недвижимости через API.
        """
        api_client.force_authenticate(admin_user)
        url = reverse("object-list")

        data = {
            "name": "New Admin Object",
            "price": 250000,
            "currency": "USD",
            "status": "sale",
            "country": "USA",
            "city": "New York",
            "address": "123 Admin Street",
            "area": 200.5,
            "rooms": 5,
            "photos": ["http://example.com/photo1.jpg"],
            "videos": ["http://example.com/video1.mp4"],
            "features": {"pool": True, "garage": True},
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == HTTP_201_CREATED
        assert response.data["name"] == "New Admin Object"

    def test_broker_can_create_own_object(self, broker, api_client):
        """
        Брокер может создать объект недвижимости, привязанный к себе.
        """
        api_client.force_authenticate(broker)
        url = reverse("object-list")

        data = {
            "name": "Broker Object",
            "price": 150000,
            "currency": "USD",
            "status": "sale",
            "country": "Country",
            "city": "City",
            "address": "456 Broker Street",
            "area": 150.0,
            "rooms": 4,
            "photos": [],
            "videos": [],
            "features": {"balcony": True},
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == HTTP_201_CREATED
        assert response.data["name"] == "Broker Object"

    def test_buyer_cannot_create_object(self, buyer, api_client):
        """
        Покупатель не может создать объект недвижимости.
        """
        api_client.force_authenticate(buyer)
        url = reverse("object-list")
        data = {
            "name": "Unauthorized Object",
            "price": 100000,
            "currency": "USD",
            "status": "sale",
            "country": "Country",
            "city": "City",
            "address": "789 Buyer Street",
            "area": 100.0,
            "rooms": 3,
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == HTTP_403_FORBIDDEN

    def test_unauthorized_user_cannot_create_object(self, api_client):
        """
        Неавторизованный пользователь не может создать объект недвижимости.
        """
        url = reverse("object-list")
        data = {
            "name": "Unauthorized Object",
            "price": 100000,
            "currency": "USD",
            "status": "sale",
            "country": "Country",
            "city": "City",
            "address": "Unknown Address",
            "area": 100.0,
            "rooms": 3,
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == HTTP_401_UNAUTHORIZED

    def test_admin_can_delete_object(self, admin_user, api_client, real_estate_object):
        """
        Администратор может удалить объект недвижимости.
        """
        api_client.force_authenticate(admin_user)
        url = reverse("object-detail", args=[real_estate_object.id])
        response = api_client.delete(url)
        assert response.status_code == HTTP_204_NO_CONTENT

    def test_broker_cannot_delete_others_object(
        self, another_broker, api_client, real_estate_object
    ):
        """
        Брокер не может удалить чужой объект недвижимости.
        """
        api_client.force_authenticate(another_broker)
        url = reverse("object-detail", args=[real_estate_object.id])
        response = api_client.delete(url)
        assert response.status_code == HTTP_403_FORBIDDEN

    def test_unauthorized_user_cannot_delete_object(
        self, api_client, real_estate_object
    ):
        """
        Неавторизованный пользователь не может удалить объект недвижимости.
        """
        url = reverse("object-detail", args=[real_estate_object.id])
        response = api_client.delete(url)
        assert response.status_code == HTTP_401_UNAUTHORIZED
