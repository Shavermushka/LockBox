# -*- coding: utf-8 -*-

"""
Модели данных для приложения.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class PasswordEntry:
    """Модель записи пароля."""
    id: Optional[int]
    title: str
    username: Optional[str]
    password: str
    url: Optional[str]
    category: Optional[str]
    notes: Optional[str]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
