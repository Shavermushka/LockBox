# -*- coding: utf-8 -*-

"""
Шифрование и дешифрование паролей с использованием Fernet.
Главный пароль используется для генерации ключа.
"""

import base64
import hashlib
import os
import logging
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)

class CryptoManager:
    """Управление шифрованием."""

    def __init__(self, master_password: Optional[str] = None):
        self.master_password = master_password
        self._fernet = None

    def set_master_password(self, password: str) -> None:
        """Установить главный пароль и инициализировать Fernet."""
        self.master_password = password
        self._fernet = None  # сбросить, чтобы пересоздать

    def _get_fernet(self) -> Fernet:
        """Получить объект Fernet на основе мастер-пароля."""
        if self._fernet is None:
            if not self.master_password:
                raise ValueError("Мастер-пароль не установлен")
            # Используем соль для дополнительной безопасности
            salt = b'fixed_salt_123456'  # В реальном приложении лучше хранить отдельно
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
            self._fernet = Fernet(key)
        return self._fernet

    def encrypt(self, plaintext: str) -> str:
        """Зашифровать строку."""
        if not plaintext:
            return ""
        fernet = self._get_fernet()
        encrypted = fernet.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Расшифровать строку."""
        if not ciphertext:
            return ""
        fernet = self._get_fernet()
        try:
            encrypted = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted = fernet.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Ошибка расшифровки: {e}")
            raise ValueError("Неверный мастер-пароль или повреждённые данные") from e
