from rest_framework.permissions import BasePermission


class IsAdminOrModerator(BasePermission):
    """
    Разрешение для проверки, является ли пользователь администратором или модератором.
    """

    def has_permission(self, request, view):
        user = request.user
        # Проверяем, что пользователь аутентифицирован и роль его профиля корректна
        return (
            user.is_authenticated
            and hasattr(user, "profile")  # Убедимся, что профиль существует
            and user.profile.role  # Убедимся, что роль задана
            and user.profile.role.name
            in ["super_admin", "admin", "moderator"]  # Сравнение по имени роли
        )


class IsBrokerOrAmbassador(BasePermission):
    """
    Разрешение для проверки, является ли пользователь брокером или амбассадором.
    """

    def has_permission(self, request, view):
        user = request.user
        # Проверяем, что пользователь аутентифицирован и роль его профиля корректна
        return (
            user.is_authenticated
            and hasattr(user, "profile")  # Убедимся, что профиль существует
            and user.profile.role  # Убедимся, что роль задана
            and user.profile.role.name
            in ["broker", "ambassador"]  # Сравнение по имени роли
        )


class IsAdminOrBroker(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser
            or request.user.profile.role.name == "broker"
            or request.user.profile.role.name == "ambassador"
        )


class IsBuyer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.profile.role.name == "buyer"
        )
