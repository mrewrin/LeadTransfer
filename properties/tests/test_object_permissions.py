import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestRealEstateObjectPermissions:
    def test_admin_full_access(self, admin_user, api_client):
        """
        Администратор имеет полный доступ к объектам недвижимости.
        """
        api_client.force_authenticate(admin_user)
        url = reverse("object-list")

        # POST - создание объекта (без поля broker)
        data = {
            "name": "Test Object",
            "price": 100000,
            "currency": "USD",
            "status": "sale",
            "country": "Country",
            "city": "City",
            "address": "Test Address",
            "area": 120.5,
            "rooms": 3,
            "photos": [],
            "videos": [],
            "features": {},
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 201, response.data  # Отладочный вывод

    def test_broker_create_own_objects(self, broker, api_client):
        """
        Брокер может создавать объекты и управлять только своими.
        """
        api_client.force_authenticate(broker)
        url = reverse("object-list")

        data = {
            "name": "Broker Object",
            "price": 200000,
            "currency": "USD",
            "status": "sale",
            "country": "Country",
            "city": "City",
            "address": "Broker Address",
            "area": 150.0,
            "rooms": 4,
            "photos": [],
            "videos": [],
            "features": {},
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 201

    def test_broker_update_own_object(self, broker, api_client, real_estate_object):
        """
        Брокер может обновлять только свои объекты недвижимости.
        """
        api_client.force_authenticate(broker)
        url = reverse("object-detail", args=[real_estate_object.id])

        data = {
            "name": "Updated Broker Object",
            "price": real_estate_object.price,
            "currency": real_estate_object.currency,
            "status": real_estate_object.status,
            "country": real_estate_object.country,
            "city": real_estate_object.city,
            "address": real_estate_object.address,
            "area": real_estate_object.area,
            "rooms": real_estate_object.rooms,
            "photos": real_estate_object.photos,
            "videos": real_estate_object.videos,
            "features": real_estate_object.features,
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == 200, response.data

    def test_broker_cannot_update_others_objects(
        self, another_broker, api_client, real_estate_object
    ):
        """
        Брокер не может обновлять чужие объекты недвижимости.
        """
        api_client.force_authenticate(another_broker)
        url = reverse("object-detail", args=[real_estate_object.id])

        data = {
            "name": "Hacked Object",
            "price": real_estate_object.price,
            "currency": real_estate_object.currency,
            "status": real_estate_object.status,
            "country": real_estate_object.country,
            "city": real_estate_object.city,
            "address": real_estate_object.address,
            "area": real_estate_object.area,
            "rooms": real_estate_object.rooms,
            "photos": real_estate_object.photos,
            "videos": real_estate_object.videos,
            "features": real_estate_object.features,
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == 403, response.data

    def test_broker_delete_own_object(self, broker, api_client, real_estate_object):
        """
        Брокер может удалять только свои объекты недвижимости.
        """
        api_client.force_authenticate(broker)
        url = reverse("object-detail", args=[real_estate_object.id])

        response = api_client.delete(url)
        assert response.status_code == 204

    def test_broker_cannot_delete_others_objects(
        self, another_broker, api_client, real_estate_object
    ):
        """
        Брокер не может удалять чужие объекты недвижимости.
        """
        api_client.force_authenticate(another_broker)
        url = reverse("object-detail", args=[real_estate_object.id])

        response = api_client.delete(url)
        assert response.status_code == 403

    def test_buyer_read_only_access(self, buyer, api_client, real_estate_object):
        """
        Покупатель имеет доступ только на чтение объектов недвижимости.
        """
        api_client.force_authenticate(buyer)
        url = reverse("object-detail", args=[real_estate_object.id])

        # GET - просмотр объекта
        response = api_client.get(url)
        assert response.status_code == 200

        # POST - создание объекта (должно быть запрещено)
        url = reverse("object-list")
        response = api_client.post(url, {"name": "Invalid"})
        assert response.status_code == 403

    def test_unauthorized_user_no_access(self, api_client, real_estate_object):
        """
        Неавторизованный пользователь имеет доступ только на чтение объектов недвижимости.
        """
        url = reverse("object-detail", args=[real_estate_object.id])

        # GET - должно быть разрешено
        response = api_client.get(url)
        assert response.status_code == 200  # Обновляем ожидаемый результат на 200

        # PUT/DELETE - должно быть запрещено
        response = api_client.put(url, {"name": "Unauthorized Update"})
        assert response.status_code == 401  # PUT должен возвращать 401
