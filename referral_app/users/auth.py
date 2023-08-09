from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class CustomAuthBackend(ModelBackend):
    """Класс бэкенда, чтобы сделать возможной авторизацию пользователя
    по отправленному коду верификации."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        username = username or kwargs.get(User.USERNAME_FIELD)
        code = kwargs.get('verification_code')
        if username is None or code is None:
            return None
        try:
            user = User._default_manager.get_by_natural_key(username)
            if user.check_code(code) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None
