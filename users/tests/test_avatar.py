import pytest
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io


@pytest.mark.django_db
class TestUserAvatarUpload:
    # def test_upload_valid_avatar(self, api_client, broker_user):
    #     """
    #     Проверка успешной загрузки аватара.
    #     """
    #     api_client.force_authenticate(user=broker_user)
    #
    #     # Создаем тестовое изображение
    #     image = Image.new("RGB", (1024, 1024), "blue")
    #     buffer = io.BytesIO()
    #     image.save(buffer, format="JPEG")
    #     buffer.seek(0)
    #
    #     avatar = SimpleUploadedFile("avatar.jpg", buffer.read(), content_type="image/jpeg")
    #     response = api_client.post("/api/auth/profile/avatar/",
    #     {"avatar": avatar}, format="multipart")
    #
    #     assert response.status_code == status.HTTP_200_OK
    #     assert "avatar_url" in response.data

    def test_upload_invalid_format(self, api_client, broker_user):
        """
        Проверка загрузки файла неподдерживаемого формата.
        """
        api_client.force_authenticate(user=broker_user)

        avatar = SimpleUploadedFile(
            "avatar.txt", b"invalid data", content_type="text/plain"
        )
        response = api_client.post(
            "/api/auth/profile/avatar/", {"avatar": avatar}, format="multipart"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"] == "Только JPEG и PNG файлы поддерживаются."

    def test_upload_unauthenticated(self, api_client):
        """
        Проверка попытки загрузки аватара без авторизации.
        """
        image = Image.new("RGB", (512, 512), "blue")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        avatar = SimpleUploadedFile(
            "avatar.png", buffer.read(), content_type="image/png"
        )
        response = api_client.post(
            "/api/auth/profile/avatar/", {"avatar": avatar}, format="multipart"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # def test_large_image_resize(self, api_client, broker_user):
    #     """
    #     Проверка автоматической обрезки и изменения размера изображения.
    #     """
    #     api_client.force_authenticate(user=broker_user)
    #
    #     # Создаем тестовое изображение большого размера
    #     image = Image.new("RGB", (2000, 2000), "red")
    #     buffer = io.BytesIO()
    #     image.save(buffer, format="JPEG")
    #     buffer.seek(0)
    #
    #     avatar = SimpleUploadedFile("large_avatar.jpg", buffer.read(), content_type="image/jpeg")
    #     response = api_client.post("/api/auth/profile/avatar/",
    #     {"avatar": avatar}, format="multipart")
    #
    #     assert response.status_code == status.HTTP_200_OK
    #     assert "avatar_url" in response.data
    #
    #     # Проверяем, что изображение обрезано до 512x512
    #     profile = broker_user.profile
    #     resized_image = Image.open(profile.avatar.path)
    #     assert resized_image.size == (512, 512)
