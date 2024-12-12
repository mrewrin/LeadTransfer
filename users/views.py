# from django.core.mail import send_mail  # Для отправки писем
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from .models import User


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": "This is a protected endpoint!"})


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # user = serializer.save()
            # Заготовка для отправки email (пока не активирована)
            # send_mail(
            #     'Подтверждение регистрации',
            #     'Ссылка для подтверждения: http://example.com/confirm',
            #     settings.DEFAULT_FROM_EMAIL,
            #     [user.email],
            # )
            return Response(
                {"message": "User registered successfully!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def verify_broker(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.is_verified = True
        user.save()
        return Response({"message": "Broker verified successfully!"})
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
