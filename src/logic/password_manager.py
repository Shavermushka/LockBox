# -*- coding: utf-8 -*-

"""
Основной менеджер паролей. Обеспечивает шифрование/дешифрование при работе с БД.
"""

import logging
from typing import List, Optional

from .database import Database
from .crypto import CryptoManager
from .models import PasswordEntry

logger = logging.getLogger(__name__)

class PasswordManager:
    """Класс для управления паролями с шифрованием."""

    def __init__(self, db: Database, crypto: CryptoManager):
        self.db = db
        self.crypto = crypto

    def set_master_password(self, password: str) -> None:
        """Установить мастер-пароль для шифрования."""
        self.crypto.set_master_password(password)

    def add_entry(self, title: str, username: str = "", password: str = "",
                  url: str = "", category: str = "", notes: str = "") -> int:
        """Добавить новую запись (пароль шифруется)."""
        encrypted_password = self.crypto.encrypt(password)
        entry = PasswordEntry(
            id=None,
            title=title,
            username=username,
            password=encrypted_password,
            url=url,
            category=category,
            notes=notes
        )
        return self.db.add_entry(entry)

    def update_entry(self, entry_id: int, title: str, username: str = "",
                     password: str = "", url: str = "", category: str = "",
                     notes: str = "") -> None:
        """Обновить запись (пароль шифруется)."""
        encrypted_password = self.crypto.encrypt(password)
        entry = PasswordEntry(
            id=entry_id,
            title=title,
            username=username,
            password=encrypted_password,
            url=url,
            category=category,
            notes=notes
        )
        self.db.update_entry(entry_id, entry)

    def get_all_entries(self) -> List[PasswordEntry]:
        """Получить все записи с зашифрованными паролями."""
        return self.db.get_all_entries()

    def get_entry_by_id(self, entry_id: int) -> Optional[PasswordEntry]:
        """Получить запись по ID (пароль зашифрован)."""
        return self.db.get_entry_by_id(entry_id)

    def get_decrypted_password(self, entry_id: int) -> str:
        """Получить расшифрованный пароль для записи."""
        entry = self.db.get_entry_by_id(entry_id)
        if not entry:
            raise ValueError("Запись не найдена")
        return self.crypto.decrypt(entry.password)

    def search_entries(self, search: str = "", category: str = "") -> List[PasswordEntry]:
        """Поиск записей (пароли остаются зашифрованными)."""
        return self.db.search_entries(search, category)

    def delete_entries(self, ids: List[int]) -> None:
        """Удалить записи."""
        self.db.delete_entries(ids)

    def get_categories(self) -> List[str]:
        """Получить список категорий."""
        return self.db.get_categories()
