from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class ApiUrlsTests(APITestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_one = User.objects.create_user(
            phone=79998887760,
            invite_code='AAa111',
        )
        cls.user_two = User.objects.create_user(
            phone=79998887761,
            invite_code='AAa112',
            granted_code='AAa111',
        )
        cls.user_three = User.objects.create_user(
            phone=79998887762,
            invite_code='AAa113',
            granted_code='AAa111',
            verification_code='1111',
            verif_cutoff_timestamp=(datetime.utcnow().timestamp()
                                    + settings.VERIF_TIME),
        )
        cls.guest_client = APIClient()
        cls.authorized_client = APIClient()
        cls.authorized_client.force_authenticate(user=cls.user_one)

    def test_urls_are_available_for_guest_get_method(self):
        """GET: Эндпойнты из списка доступны неавторизованному
        пользователю."""
        urls_for_guest = [
            ('/api/users/', 200),
            (f'/api/users/{self.user_one.id}/', 200),
        ]
        for each_url, code in urls_for_guest:
            with self.subTest(each_url=each_url):
                response = self.guest_client.get(each_url)
                self.assertEqual(response.status_code, code)

    def test_urls_are_available_for_guest_post_method(self):
        """POST: Эндпойнты регистрации и верификации доступны
        неавторизованному пользователю."""
        registration_data = {'phone': 79998887764}
        verif_data = {
            'phone': self.user_three.phone,
            'verification_code': self.user_three.verification_code
        }
        urls_for_guest = [
            ('/api/auth/registration/', registration_data, 201),
            ('/api/auth/verification/', verif_data, 200)

        ]
        for each_url, data, code in urls_for_guest:
            with self.subTest(each_url=each_url):
                response = self.guest_client.post(
                    each_url,
                    data=data,
                    format='json',
                )
                self.assertEqual(response.status_code, code)

    def test_urls_are_available_for_authorized_patch_method(self):
        """PATCH: Эндпойнты из списка доступны авторизованному
        пользователю."""
        user_change_data = {'granted_code': 'AAa112'}

        urls_for_authorized = [
            (f'/api/users/{self.user_one.id}/', user_change_data, 200),
        ]
        for each_url, data, code in urls_for_authorized:
            with self.subTest(each_url=each_url):
                response = self.authorized_client.patch(
                    each_url,
                    data=data,
                    format='json',
                )
                self.assertEqual(response.status_code, code)
