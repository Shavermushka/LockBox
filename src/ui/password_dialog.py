# -*- coding: utf-8 -*-

"""
Диалог добавления/редактирования записи пароля.
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QPushButton, QLabel, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import Qt
from src.logic.models import PasswordEntry

class PasswordDialog(QDialog):
    """Диалог для ввода данных пароля."""

    def __init__(self, parent=None, entry: Optional[PasswordEntry] = None) -> None:
        super().__init__(parent)
        self.entry = entry
        self.setWindowTitle("Редактирование" if entry else "Новый пароль")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Название (например, Google)")
        form.addRow("Название:", self.title_edit)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Логин или email")
        form.addRow("Логин:", self.username_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Пароль")
        form.addRow("Пароль:", self.password_edit)

        # Кнопка генерации пароля
        gen_btn = QPushButton("Сгенерировать")
        gen_btn.clicked.connect(self._generate_password)
        self.password_edit_layout = QHBoxLayout()
        self.password_edit_layout.addWidget(self.password_edit)
        self.password_edit_layout.addWidget(gen_btn)
        form.addRow("Пароль:", self.password_edit_layout)

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://example.com")
        form.addRow("URL:", self.url_edit)

        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("Категория")
        form.addRow("Категория:", self.category_edit)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Дополнительные заметки")
        self.notes_edit.setMaximumHeight(80)
        form.addRow("Заметки:", self.notes_edit)

        layout.addLayout(form)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Сохранить")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        # Заполнение если редактируем
        if entry:
            self.title_edit.setText(entry.title)
            self.username_edit.setText(entry.username or "")
            self.password_edit.setText(entry.password or "")
            self.url_edit.setText(entry.url or "")
            self.category_edit.setText(entry.category or "")
            self.notes_edit.setText(entry.notes or "")

    def _generate_password(self) -> None:
        """Генерация пароля и вставка в поле."""
        from src.utils.helpers import generate_password
        try:
            password = generate_password(16, True, True, True, True)
            self.password_edit.setText(password)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сгенерировать пароль:\n{e}")

    def get_data(self) -> dict:
        """Возвращает словарь с данными из формы."""
        return {
            "title": self.title_edit.text().strip(),
            "username": self.username_edit.text().strip(),
            "password": self.password_edit.text(),
            "url": self.url_edit.text().strip(),
            "category": self.category_edit.text().strip(),
            "notes": self.notes_edit.toPlainText().strip(),
        }

    def accept(self) -> None:
        """Проверка перед сохранением."""
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Ошибка", "Название обязательно.")
            return
        if not self.password_edit.text():
            QMessageBox.warning(self, "Ошибка", "Пароль не может быть пустым.")
            return
        super().accept()
