#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Главный модуль приложения Password Manager.
Запускает QApplication и главное окно.
"""

import sys
import os
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings, Qt

from src.main_window import MainWindow
from src.utils.logger import setup_logging
from src.logic.database import Database
from src.logic.crypto import CryptoManager

def main() -> None:
    """Точка входа в приложение."""
    # Настройка логирования
    log_dir = Path.home() / ".password_manager" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(log_dir / "app.log")

    app = QApplication(sys.argv)
    app.setApplicationName("Password Manager")
    app.setOrganizationName("YourOrg")

    # Инициализация основных компонентов
    db = Database()
    crypto = CryptoManager()

    # Загрузка настроек
    settings = QSettings()
    theme = settings.value("theme", "dark", type=str)

    # Применение стиля
    style_path = Path(__file__).parent / "src" / "resources" / "styles" / f"{theme}.qss"
    if style_path.exists():
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    window = MainWindow(db, crypto)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
