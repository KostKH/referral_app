import random
import string


def generate_sequense(length, digits_only=False):
    """Функция для генерации случайной последовательности букв и цифр."""
    if digits_only:
        symbols = string.digits
    else:
        symbols = string.ascii_letters + string.digits
    result = [random.sample(symbols, 1)[0] for _ in range(length)]
    return ''.join(result)
