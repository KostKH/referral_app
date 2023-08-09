from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class ApiViewsTests(APITestCase):

    def setUp(self):
        self.user_one = User.objects.create_user(
            phone=79998887760,
            invite_code='AAa111',
        )
        self.user_two = User.objects.create_user(
            phone=79998887761,
            invite_code='AAa112',
            granted_code='AAa111',
        )
        self.user_three = User.objects.create_user(
            phone=79998887762,
            invite_code='AAa113',
            granted_code='AAa111',
            verification_code='2222',
            verif_cutoff_timestamp=(datetime.utcnow().timestamp()
                                    + settings.VERIF_TIME),
        )
        self.user_four = User.objects.create_user(
            phone=79998887763,
            verification_code='1111',
            verif_cutoff_timestamp=(datetime.utcnow().timestamp()
                                    + settings.VERIF_TIME),
        )
        self.guest_client = APIClient()
        self.authorized_client = APIClient()
        self.authorized_client.force_authenticate(user=self.user_one)
        self.authorized_client2 = APIClient()
        self.authorized_client2.force_authenticate(user=self.user_two)

    def test_api_regiser_post_returns_correct_data(self):
        """Метод POST Эндпойнта api-register отдает правильный ответ."""
        user_data = {
            'phone': 79998887765,
        }
        response = self.guest_client.post(
            reverse('api-register'),
            data=user_data,
            format='json'
        )
        expected_user = User.objects.all().order_by('-id').first()
        expected_keys = sorted(
            [
                'id',
                'phone',
            ]
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(sorted(response.data.keys()), expected_keys)
        for key, response_value in response.data.items():
            with self.subTest(key=key):
                expected_value = getattr(expected_user, key)
                self.assertEqual(response_value, expected_value)

    def test_api_regiser_post_invalid_data_fails(self):
        """Метод POST Эндпойнта api-regiser при отправке некорректных данных
        не создает пользователя и возвращает код 400."""
        len_users_before = len(User.objects.all())
        incorrect_data_list = [
            {'phone': 'text'},
            {'phone': -79998887766},
            {'email': 'aa@bb.cc'},
            {},
        ]
        for invalid_data in incorrect_data_list:
            with self.subTest(data=str(invalid_data)):
                response = self.guest_client.post(
                    reverse('api-register'),
                    data=invalid_data,
                    format='json')
                len_users_after = len(User.objects.all())
                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST)
                self.assertEqual(len_users_before, len_users_after)

    def test_api_register_invalid_methods_not_allowed(self):
        """Эндпойнт api-register не принимает запросы
        с неразрешенными методами."""
        methods = ['GET', 'PUT', 'PATCH', 'DELETE']
        len_users_before = len(User.objects.all())

        for method in methods:
            with self.subTest(method=method):
                request_method = getattr(self.guest_client, method.lower())
                response = request_method(reverse('api-register'))
                len_users_after = len(User.objects.all())
                self.assertEqual(
                    response.status_code,
                    status.HTTP_405_METHOD_NOT_ALLOWED)
                self.assertEqual(len_users_before, len_users_after)

    def test_api_user_list_get_returns_correct_data(self):
        """Метод GET Эндпойнта api-user-list отдает правильный ответ."""
        response = self.guest_client.get(reverse('api-user-list'))
        expected_users = User.objects.all().order_by('-id')
        expected_keys = sorted(
            [
                'id',
                'phone',
                'email',
                'first_name',
                'last_name',
                'invite_code',
                'granted_code',
            ]
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(expected_users))
        for user_idx, response_user in enumerate(response.data):
            self.assertEqual(sorted(response_user.keys()), expected_keys)
            for key, response_value in response_user.items():
                expected_value = getattr(expected_users[user_idx], key)
                self.assertEqual(response_value, expected_value)

    def test_api_user_list_invalid_methods_not_allowed(self):
        """Эндпойнт api-user-list не принимает запросы
        с неразрешенными методами."""
        methods = ['POST', 'PUT', 'PATCH', 'DELETE']
        for method in methods:
            with self.subTest(method=method):
                request_method = getattr(
                    self.authorized_client,
                    method.lower()
                )
                response = request_method(reverse('api-user-list'))
                self.assertEqual(
                    response.status_code,
                    status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_api_user_detail_get_returns_correct_data(self):
        """Метод GET Эндпойнта api_user_detail отдает правильный ответ."""
        response = self.guest_client.get(
            reverse('api-user-detail', args=[self.user_one.id]))
        expected_code_applicants = (
            User.objects.values('phone')
            .filter(granted_code=self.user_one.invite_code)
            .order_by('phone')
        )
        expected_keys = sorted(
            [
                'id',
                'phone',
                'email',
                'first_name',
                'last_name',
                'invite_code',
                'granted_code',
                'code_applicants',
            ]
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(sorted(response.data.keys()), expected_keys)
        for key, response_value in response.data.items():
            if key == 'code_applicants':
                continue
            expected_value = getattr(self.user_one, key)
            self.assertEqual(response_value, expected_value)
        for idx, item in enumerate(response.data['code_applicants']):
            self.assertEqual(len(item.keys()), 1)
            self.assertEqual(
                item['phone'],
                expected_code_applicants[idx]['phone'],
            )

    def test_api_user_detail_invalid_methods_not_allowed(self):
        """Эндпойнт api-user-detail не принимает запросы
        с неразрешенными методами."""
        methods = ['POST', 'DELETE']

        for method in methods:
            with self.subTest(method=method):
                request_method = getattr(
                    self.authorized_client,
                    method.lower(),
                )
                response = request_method(
                    reverse('api-user-detail', args=[self.user_one.id]))
                self.assertEqual(
                    response.status_code,
                    status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_api_user_detail_patch_returns_correct_data(self):
        """PATCH api_user_detail: метод отдает правильный ответ."""

        data = {
            'email': 'aa@bb.cc',
            'first_name': 'John',
            'last_name': 'Smith',
            'granted_code': self.user_two.invite_code,
        }
        expected_data = {
            'id': self.user_one.id,
            'phone': self.user_one.phone,
            'email': data.get('email'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'invite_code': self.user_one.invite_code,
            'granted_code': data.get('granted_code'),
        }
        expected_keys = sorted(expected_data.keys())
        response = self.authorized_client.patch(
            reverse('api-user-detail', args=[self.user_one.id]),
            data=data,
            format='json')
        updated_user = User.objects.get(id=self.user_one.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(sorted(response.data.keys()), expected_keys)
        for key, response_value in response.data.items():
            with self.subTest(key=key):
                self.assertEqual(response_value, expected_data.get(key))
                updated_user_value = getattr(updated_user, key)
                self.assertEqual(updated_user_value, expected_data.get(key))

    def test_api_user_detail_patch_non_self_fails(self):
        """PATCH api_user_detail: только свои данные могут быть изменены
        пользователем."""

        data = {
            'email': 'aa@bb.cc',
            'first_name': 'John',
            'last_name': 'Smith',
            'granted_code': self.user_two.invite_code,
        }
        response = self.authorized_client2.patch(
            reverse('api-user-detail', args=[self.user_one.id]),
            data=data,
            format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_user_detail_patch_granted_code_only_once(self):
        """PATCH api_user_detail: полученный инвайт-код может быть введен
        только один раз."""
        data = {'granted_code': self.user_two.invite_code}
        response = self.authorized_client.patch(
            reverse('api-user-detail', args=[self.user_one.id]),
            data=data,
            format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('granted_code'),
                         self.user_two.invite_code)
        updated_user = User.objects.get(id=self.user_one.id)
        self.assertEqual(updated_user.granted_code,
                         self.user_two.invite_code)

    def test_api_user_detail_patch_invalid_granted_code_fails(self):
        """PATCH api_user_detail: невалидный полученный инвайт-код не может
        быть введен."""
        granted_code_before = self.user_one.granted_code
        invalid_data_list = [
            {'granted_code': self.user_one.invite_code},
            {'granted_code': 'AAa000'},
            {'granted_code': 'AAa0000'},
        ]
        for invalid_data in invalid_data_list:
            response = self.authorized_client.patch(
                reverse('api-user-detail', args=[self.user_one.id]),
                data=invalid_data,
                format='json')
            granted_code_after = (User.objects
                                  .get(id=self.user_one.id)
                                  .granted_code)
            with self.subTest(invalid_data=str(invalid_data)):
                self.assertEqual(response.status_code,
                                 status.HTTP_400_BAD_REQUEST)
                self.assertEqual(granted_code_before, granted_code_after)

    def test_api_user_detail_patch_phone_invate_code_fails(self):
        """PATCH api_user_detail: пользователь не может менять телефон и
        инвайт-код."""
        phone_before = self.user_one.phone
        invite_code_before = self.user_one.invite_code
        data = {
            'phone': 79998887780,
            'invite_code': 'Aaa000',
            'email': 'aa@bb.cc',
        }
        response = self.authorized_client.patch(
            reverse('api-user-detail', args=[self.user_one.id]),
            data=data,
            format='json')
        updated_user = User.objects.get(id=self.user_one.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(updated_user.phone, phone_before)
        self.assertEqual(updated_user.invite_code, invite_code_before)

    def test_api_verification_invalid_methods_not_allowed(self):
        """Эндпойнт api-verification не принимает запросы
        с неразрешенными методами."""
        methods = ['GET', 'PUT', 'PATCH', 'DELETE']

        for method in methods:
            with self.subTest(method=method):
                request_method = getattr(self.guest_client, method.lower())
                response = request_method(
                    reverse('api-verification'))
                self.assertEqual(
                    response.status_code,
                    status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_api_verification_post_returns_correct_data(self):
        """POST api-verification: метод отдает правильный ответ."""
        user_data = {
            'phone': self.user_four.phone,
            'verification_code': self.user_four.verification_code
        }
        invite_code_before = self.user_four.invite_code
        response = self.guest_client.post(
            reverse('api-verification'),
            data=user_data,
            format='json'
        )
        expected_token = Token.objects.get(user_id=self.user_four.id).key
        expected_keys = ['token']
        invite_code_after = User.objects.get(id=self.user_four.id).invite_code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(sorted(response.data.keys()), expected_keys)
        self.assertEqual(response.data.get('token'), expected_token)
        self.assertNotEqual(invite_code_before, invite_code_after)

    def test_api_verification_post_invite_code_is_created_once(self):
        """POST api-verification: инвайт-код создается только один раз."""
        user_data = {
            'phone': self.user_three.phone,
            'verification_code': self.user_three.verification_code
        }
        invite_code_before = self.user_three.invite_code
        response = self.guest_client.post(
            reverse('api-verification'),
            data=user_data,
            format='json'
        )
        invite_code_after = (User.objects
                             .get(id=self.user_three.id)
                             .invite_code)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(invite_code_before, invite_code_after)

    def test_api_verification_post_invalid_data_fails(self):
        """POST api-verification: невалидные данные не приводят
        к авториззации и созданию инвайт-кода."""
        invite_code_before = self.user_four.invite_code
        invalid_data_list = [
            {
                'phone': self.user_four.phone,
                'verification_code': 1112
            },
            {
                'phone': self.user_four.phone,
            },
            {
                'verification_code': self.user_four.verification_code
            },
            {
                'phone': 79998887790,
                'verification_code': self.user_four.verification_code
            },
            {
                'phone': self.user_four.phone,
                'verification_code': ''
            },
            {
                'phone': self.user_four.phone,
                'verification_code': '9999'
            },
        ]
        for invalid_data in invalid_data_list:
            response = self.guest_client.post(
                reverse('api-verification'),
                data=invalid_data,
                format='json')
            invite_code_after = (User.objects
                                 .get(id=self.user_four.id)
                                 .invite_code)
            with self.subTest(invalid_data=str(invalid_data)):
                self.assertEqual(response.status_code,
                                 status.HTTP_400_BAD_REQUEST)
                self.assertEqual(invite_code_before, invite_code_after)
