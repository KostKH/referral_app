from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Верификация для изменения данных о пользователе.Проверяем
    в небезопасных методах, что пользователь может изменять только
    свои данные."""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj == request.user)
