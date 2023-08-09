from django.test import TestCase

from users.utils import generate_sequense


class UserUtilsTests(TestCase):

    def test_generate_sequense_digits_and_letters(self):
        """Проверяем, что функция generate_sequense возвращает
        последовательность заданной длины с буквами и цифрами."""

        expected_lengthes = [15, 10, 25, 3, 4, 6]
        for expected_length in expected_lengthes:
            sequence = generate_sequense(expected_length)
            self.assertEqual(len(sequence), expected_length)
            self.assertFalse(sequence.isdigit())
            self.assertTrue(sequence.isalnum())

    def test_generate_sequense_digits_only(self):
        """Проверяем, что функция generate_sequense возвращает
        последовательность заданной длины только с цифрами."""

        expected_lengthes = [18, 9, 24, 3, 4, 6]
        for expected_length in expected_lengthes:
            sequence = generate_sequense(expected_length, digits_only=True)
            self.assertEqual(len(sequence), expected_length)
            self.assertTrue(sequence.isdigit())
