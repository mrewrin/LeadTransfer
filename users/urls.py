from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import (
    protected_view,
    verify_broker,
    CustomTokenObtainPairView,
    RegisterView,
)


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("protected/", protected_view, name="protected"),
    path("verify-broker/<int:user_id>/", verify_broker, name="verify_broker"),
]