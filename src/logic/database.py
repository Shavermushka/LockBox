# -*- coding: utf-8 -*-

"""
Работа с базой данных SQLite.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from contextlib import contextmanager

from .models import PasswordEntry

logger = logging.getLogger(__name__)

class Database:
    """Класс для управления SQLite базой данных."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        if db_path is None:
            db_dir = Path.home() / ".password_manager"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "passwords.db"
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для соединения с БД."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Инициализация таблиц, если их нет."""
        with self.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    username TEXT,
                    password TEXT NOT NULL,
                    url TEXT,
                    category TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Триггер для обновления updated_at
            conn.execute('''
                CREATE TRIGGER IF NOT EXISTS update_password_updated_at
                AFTER UPDATE ON passwords
                BEGIN
                    UPDATE passwords SET updated_at = CURRENT_TIMESTAMP
                    WHERE id = NEW.id;
                END;
            ''')
            conn.commit()
            logger.info("База данных инициализирована")

    def add_entry(self, entry: PasswordEntry) -> int:
        """Добавление записи."""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO passwords (title, username, password, url, category, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (entry.title, entry.username, entry.password, entry.url, entry.category, entry.notes))
            conn.commit()
            return cursor.lastrowid

    def get_all_entries(self) -> List[PasswordEntry]:
        """Получить все записи."""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM passwords ORDER BY title')
            rows = cursor.fetchall()
            return [self._row_to_entry(row) for row in rows]

    def get_entry_by_id(self, entry_id: int) -> Optional[PasswordEntry]:
        """Получить запись по ID."""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT * FROM passwords WHERE id = ?', (entry_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_entry(row)
            return None

    def search_entries(self, search: str = "", category: str = "") -> List[PasswordEntry]:
        """Поиск записей по названию, логину, URL и категории."""
        query = 'SELECT * FROM passwords WHERE 1=1'
        params = []
        if search:
            query += ' AND (title LIKE ? OR username LIKE ? OR url LIKE ?)'
            like = f'%{search}%'
            params.extend([like, like, like])
        if category:
            query += ' AND category LIKE ?'
            params.append(f'%{category}%')
        query += ' ORDER BY title'
        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_entry(row) for row in rows]

    def update_entry(self, entry_id: int, entry: PasswordEntry) -> None:
        """Обновление записи."""
        with self.get_connection() as conn:
            conn.execute('''
                UPDATE passwords
                SET title = ?, username = ?, password = ?, url = ?, category = ?, notes = ?
                WHERE id = ?
            ''', (entry.title, entry.username, entry.password, entry.url, entry.category, entry.notes, entry_id))
            conn.commit()

    def delete_entries(self, ids: List[int]) -> None:
        """Удаление записей по списку ID."""
        if not ids:
            return
        placeholders = ','.join('?' * len(ids))
        with self.get_connection() as conn:
            conn.execute(f'DELETE FROM passwords WHERE id IN ({placeholders})', ids)
            conn.commit()

    def get_categories(self) -> List[str]:
        """Получить список всех категорий."""
        with self.get_connection() as conn:
            cursor = conn.execute('SELECT DISTINCT category FROM passwords WHERE category IS NOT NULL AND category != ""')
            rows = cursor.fetchall()
            return [row['category'] for row in rows]

    def _row_to_entry(self, row) -> PasswordEntry:
        """Преобразование строки БД в объект PasswordEntry."""
        return PasswordEntry(
            id=row['id'],
            title=row['title'],
            username=row['username'],
            password=row['password'],
            url=row['url'],
            category=row['category'],
            notes=row['notes'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
