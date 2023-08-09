from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from users.auth import CustomAuthBackend

User = get_user_model()


class UserAuthTests(TestCase):

    def setUp(self):
        self.backend = CustomAuthBackend()
        self.user_one = User.objects.create_user(
            phone=79998887760,
            verification_code='2222',
            verif_cutoff_timestamp=(datetime.utcnow().timestamp() - 60),
        )
        self.user_two = User.objects.create_user(
            phone=79998887761,
            verification_code='2222',
            verif_cutoff_timestamp=(datetime.utcnow().timestamp() + 60),
        )

    def test_custom_auth_backend_authenticates_correcttly(self):
        """Проверяем, что метод authenticate бэкенда корректно авторизует
        пользователя."""
        class MockRequest:
            pass
        request = MockRequest()
        data = {
            'phone': self.user_two.phone,
            'verification_code': self.user_two.verification_code,
        }
        user = self.backend.authenticate(request, **data)
        self.assertIsNotNone(user)
        self.assertTrue(user.is_authenticated)

    def test_custom_auth_backend_rejects_incorrect_data(self):
        """Проверяем, что метод authenticate бэкенда проваливает авторизацию,
        когда входные данные - неправильные или срок кода истек."""
        class MockRequest:
            pass
        request = MockRequest()
        invalid_data_list = [
            {
                'phone': self.user_two.phone,
                'verification_code': 1112
            },
            {
                'phone': self.user_two.phone,
            },
            {
                'verification_code': self.user_two.verification_code
            },
            {
                'phone': 79998887790,
                'verification_code': self.user_two.verification_code
            },
            {
                'phone': self.user_two.phone,
                'verification_code': ''
            },
            {
                'phone': self.user_two.phone,
                'verification_code': '9999'
            },
            {
                'phone': self.user_one.phone,
                'verification_code': self.user_one.verification_code
            },
        ]
        for data in invalid_data_list:
            with self.subTest(invalid_data=str(data)):
                user = self.backend.authenticate(request, **data)
                self.assertIsNone(user)
