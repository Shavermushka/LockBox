# -*- coding: utf-8 -*-

"""
Импорт и экспорт данных в различных форматах.
"""

import json
import csv
import logging
from typing import List, Dict, Any
from pathlib import Path

import yaml
import pandas as pd

from .password_manager import PasswordManager
from .models import PasswordEntry

logger = logging.getLogger(__name__)

class ImportExport:
    """Класс для импорта/экспорта паролей."""

    def __init__(self, password_manager: PasswordManager):
        self.pm = password_manager

    def export_json(self, file_path: str) -> None:
        """Экспорт в JSON (пароли шифрованные)."""
        entries = self.pm.get_all_entries()
        data = [self._entry_to_dict(e) for e in entries]
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_json(self, file_path: str) -> int:
        """Импорт из JSON (ожидаются шифрованные пароли)."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        count = 0
        for item in data:
            self.pm.add_entry(
                title=item.get('title', ''),
                username=item.get('username', ''),
                password=item.get('password', ''),
                url=item.get('url', ''),
                category=item.get('category', ''),
                notes=item.get('notes', '')
            )
            count += 1
        return count

    def export_csv(self, file_path: str) -> None:
        """Экспорт в CSV."""
        entries = self.pm.get_all_entries()
        data = [self._entry_to_dict(e) for e in entries]
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'username', 'password', 'url', 'category', 'notes'])
            writer.writeheader()
            writer.writerows(data)

    def import_csv(self, file_path: str) -> int:
        """Импорт из CSV."""
        count = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.pm.add_entry(
                    title=row.get('title', ''),
                    username=row.get('username', ''),
                    password=row.get('password', ''),
                    url=row.get('url', ''),
                    category=row.get('category', ''),
                    notes=row.get('notes', '')
                )
                count += 1
        return count

    def export_excel(self, file_path: str) -> None:
        """Экспорт в Excel."""
        entries = self.pm.get_all_entries()
        data = [self._entry_to_dict(e) for e in entries]
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False, sheet_name='Passwords')

    def import_excel(self, file_path: str) -> int:
        """Импорт из Excel."""
        df = pd.read_excel(file_path)
        count = 0
        for _, row in df.iterrows():
            self.pm.add_entry(
                title=str(row.get('title', '')),
                username=str(row.get('username', '')),
                password=str(row.get('password', '')),
                url=str(row.get('url', '')),
                category=str(row.get('category', '')),
                notes=str(row.get('notes', ''))
            )
            count += 1
        return count

    def export_yaml(self, file_path: str) -> None:
        """Экспорт в YAML."""
        entries = self.pm.get_all_entries()
        data = [self._entry_to_dict(e) for e in entries]
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

    def import_yaml(self, file_path: str) -> int:
        """Импорт из YAML."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        count = 0
        for item in data:
            self.pm.add_entry(
                title=item.get('title', ''),
                username=item.get('username', ''),
                password=item.get('password', ''),
                url=item.get('url', ''),
                category=item.get('category', ''),
                notes=item.get('notes', '')
            )
            count += 1
        return count

    @staticmethod
    def _entry_to_dict(entry: PasswordEntry) -> Dict[str, Any]:
        return {
            'title': entry.title,
            'username': entry.username,
            'password': entry.password,
            'url': entry.url,
            'category': entry.category,
            'notes': entry.notes
        }
