import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK


@pytest.mark.django_db
class TestRealEstateObjectFilters:
    def test_filter_by_price(self, api_client, real_estate_objects):
        """
        Проверка фильтрации объектов по минимальной и максимальной цене.
        """
        url = reverse("object-list")

        # Фильтрация по минимальной цене
        response = api_client.get(url, {"price_min": 110000})
        assert response.status_code == HTTP_200_OK
        assert len(response.data["results"]) == 1  # Только объект с ценой >= 110000

        # Фильтрация по максимальной цене
        response = api_client.get(url, {"price_max": 130000})
        assert response.status_code == HTTP_200_OK
        assert len(response.data["results"]) == 1  # Только объект с ценой <= 130000

        # Фильтрация по диапазону цены
        response = api_client.get(url, {"price_min": 100000, "price_max": 150000})
        assert response.status_code == HTTP_200_OK
        assert len(response.data["results"]) == 2  # Оба объекта попадают в диапазон

    def test_filter_by_status(self, api_client, real_estate_objects):
        """
        Проверка фильтрации объектов по статусу (sale, rent, sold).
        """
        url = reverse("object-list")

        response = api_client.get(url, {"status": "sale"})
        assert response.status_code == HTTP_200_OK
        assert all(obj["status"] == "sale" for obj in response.data["results"])

        response = api_client.get(url, {"status": "rent"})
        assert response.status_code == HTTP_200_OK
        assert all(obj["status"] == "rent" for obj in response.data["results"])

    def test_filter_by_country(self, api_client, real_estate_objects):
        """
        Проверка фильтрации объектов по стране.
        """
        url = reverse("object-list")

        response = api_client.get(url, {"country": "Country"})
        print(response.data)  # Убедитесь, что фильтры применены правильно

        assert response.status_code == HTTP_200_OK
        assert len(response.data["results"]) == 2  # Оба объекта из "Country"

        # Проверка с разным регистром
        response = api_client.get(url, {"country": "cOuNtRy"})
        assert response.status_code == HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_sorting(self, api_client, real_estate_objects):
        """
        Проверка сортировки объектов по цене и дате создания.
        """
        url = reverse("object-list")

        response = api_client.get(url, {"ordering": "price"})
        assert response.status_code == HTTP_200_OK
        prices = [obj["price"] for obj in response.data["results"]]
        assert prices == sorted(prices)

        response = api_client.get(url, {"ordering": "-price"})
        assert response.status_code == HTTP_200_OK
        prices = [obj["price"] for obj in response.data["results"]]
        assert prices == sorted(prices, reverse=True)
