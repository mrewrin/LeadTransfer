from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from .views import (
    protected_view,
    verify_broker,
    CustomTokenObtainPairView,
    RegisterView,
    UserProfileView,
    UserVerificationView,
    AssignRoleView,
    AdminOrModeratorView,
    BrokerOrAmbassadorView,
    ChangePasswordView,
)


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("protected/", protected_view, name="protected"),
    path("verify-broker/<int:user_id>/", verify_broker, name="verify_broker"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),
    path("profile/verify/", UserVerificationView.as_view(), name="user-verification"),
    path("assign-role/", AssignRoleView.as_view(), name="assign_role"),
    path(
        "admin-or-moderator/", AdminOrModeratorView.as_view(), name="admin-or-moderator"
    ),
    path(
        "broker-or-ambassador/",
        BrokerOrAmbassadorView.as_view(),
        name="broker-or-ambassador",
    ),
]
