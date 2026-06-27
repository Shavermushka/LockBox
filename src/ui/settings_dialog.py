# -*- coding: utf-8 -*-

"""
Диалог настроек приложения.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QPushButton, QHBoxLayout, QLabel
)
from PyQt6.QtCore import QSettings

class SettingsDialog(QDialog):
    """Диалог настроек."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setMinimumWidth(400)

        settings = QSettings()
        self.current_theme = settings.value("theme", "dark", type=str)

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(self.current_theme)
        form.addRow("Тема:", self.theme_combo)

        layout.addLayout(form)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Применить")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def get_theme(self) -> str:
        """Возвращает выбранную тему."""
        return self.theme_combo.currentText()

    def accept(self) -> None:
        """Сохранить настройки."""
        theme = self.get_theme()
        QSettings().setValue("theme", theme)
        super().accept()
