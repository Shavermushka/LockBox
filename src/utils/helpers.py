# -*- coding: utf-8 -*-

"""
Вспомогательные функции.
"""

import string
import secrets
from typing import Optional

def generate_password(length: int = 16,
                      use_lower: bool = True,
                      use_upper: bool = True,
                      use_digits: bool = True,
                      use_symbols: bool = True) -> str:
    """
    Генерация безопасного пароля.

    Args:
        length: Длина пароля
        use_lower: Включать строчные буквы
        use_upper: Включать заглавные
        use_digits: Включать цифры
        use_symbols: Включать спецсимволы

    Returns:
        Сгенерированный пароль
    """
    if length < 4:
        raise ValueError("Длина должна быть не менее 4")
    chars = ""
    if use_lower:
        chars += string.ascii_lowercase
    if use_upper:
        chars += string.ascii_uppercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not chars:
        raise ValueError("Не выбрано ни одного набора символов")

    # Гарантируем хотя бы один символ из каждого выбранного набора
    password = []
    if use_lower:
        password.append(secrets.choice(string.ascii_lowercase))
    if use_upper:
        password.append(secrets.choice(string.ascii_uppercase))
    if use_digits:
        password.append(secrets.choice(string.digits))
    if use_symbols:
        password.append(secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))

    # Заполняем оставшуюся длину случайными символами
    remaining = length - len(password)
    for _ in range(remaining):
        password.append(secrets.choice(chars))

    # Перемешиваем
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)
