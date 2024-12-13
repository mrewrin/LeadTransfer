import pytest
from rest_framework.reverse import reverse
from rest_framework import status


@pytest.mark.django_db
def test_admin_access_to_admin_view(authenticated_client):
    """Тест доступа администратора к защищенному эндпоинту."""
    url = reverse("admin-or-moderator")
    response = authenticated_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "Welcome, Admin or Moderator!"
