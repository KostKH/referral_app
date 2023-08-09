from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserModelsTests(TestCase):

    def setUp(self):
        self.user_one = User.objects.create_user(
            phone=79998887760,
            verification_code='2222',
            verif_cutoff_timestamp=(datetime.utcnow().timestamp() - 60),
        )
        self.user_two = User.objects.create_user(
            phone=79998887761,
            invite_code='AAa111',
            verification_code='2222',
            verif_cutoff_timestamp=(datetime.utcnow().timestamp() + 60),
        )

    def test_verbose_name(self):
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        field_verboses = [
            (self.user_one, 'phone', 'Номер телефона'),
            (self.user_one, 'email', _('email address')),
            (self.user_one, 'verification_code', 'Код верификации'),
            (self.user_one, 'verif_cutoff_timestamp', 'Срок действия кода'),
            (self.user_one, 'invite_code', 'Инвайт-код'),
            (self.user_one, 'granted_code', 'Полученный инвайт-код'),
        ]
        for item, field, expected_value in field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    item._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_user_str_method_returns_phone(self):
        """Проверяем, что метод str возвращает Номер телефона."""
        self.assertEqual(str(self.user_one), str(self.user_one.phone))

    def test_user_check_code_method_returns_correct_result(self):
        """Проверяем, что метод check_code возвращает правильное значение."""
        test_data = [
            (self.user_one, '2222', False),
            (self.user_two, '1111', False),
            (self.user_two, '2222', True),
        ]
        for instance, code, expected_result in test_data:
            check_result = instance.check_code(code)
            self.assertEqual(check_result, expected_result)

    def test_user_create_invite_code_saves_code(self):
        """Проверяем, что метод create_invite_code создает код."""
        self.assertFalse(self.user_one.invite_code)
        self.user_one.create_invite_code()
        self.assertTrue(self.user_one.invite_code)

    def test_user_create_invite_code_saves_only_once(self):
        """Проверяем, что метод create_invite_code создает только один раз."""
        self.assertTrue(self.user_two.invite_code)
        invite_code_before = self.user_two.invite_code
        self.user_two.create_invite_code()
        invite_code_after = User.objects.get(id=self.user_two.id).invite_code
        self.assertEqual(invite_code_before, invite_code_after)
