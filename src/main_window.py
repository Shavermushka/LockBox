# Copyright (C) 2026 Егор (твой GitHub-ник)
# This file is part of [Название проекта] and is licensed under the GNU GPLv3.
# See the LICENSE file for details.

# -*- coding: utf-8 -*-

"""
Главное окно приложения. Содержит вкладки и панель инструментов.
"""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QToolBar, QStatusBar, QMessageBox,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMenu, QLabel, QApplication
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QThread, QSettings
from PyQt6.QtGui import QAction, QIcon, QKeySequence

from src.ui.password_dialog import PasswordDialog
from src.ui.settings_dialog import SettingsDialog
from src.ui.stats_widget import StatsWidget
from src.ui.network_scanner import NetworkScannerWidget
from src.logic.password_manager import PasswordManager
from src.logic.database import Database
from src.logic.crypto import CryptoManager
from src.logic.import_export import ImportExport
from src.utils.helpers import generate_password

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self, db: Database, crypto: CryptoManager) -> None:
        super().__init__()
        self.db = db
        self.crypto = crypto
        self.password_manager = PasswordManager(db, crypto)
        self.import_export = ImportExport(self.password_manager)
        self.current_theme = QSettings().value("theme", "dark", type=str)

        self.setWindowTitle("Password Manager")
        self.setMinimumSize(900, 600)

        self._setup_ui()
        self._load_passwords()

    def _setup_ui(self) -> None:
        """Настройка интерфейса."""
        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)

        # Вкладки
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Вкладка "Пароли"
        self.passwords_tab = self._create_passwords_tab()
        self.tabs.addTab(self.passwords_tab, "Пароли")

        # Вкладка "Генератор"
        self.generator_tab = self._create_generator_tab()
        self.tabs.addTab(self.generator_tab, "Генератор")

        # Вкладка "Статистика"
        self.stats_tab = StatsWidget(self.password_manager)
        self.tabs.addTab(self.stats_tab, "Статистика")

        # Вкладка "Инструменты"
        self.tools_tab = self._create_tools_tab()
        self.tabs.addTab(self.tools_tab, "Инструменты")

        # Панель инструментов
        self._create_toolbar()

        # Строка состояния
        self.statusBar().showMessage("Готов")

        # Настройка тем
        self.apply_theme(self.current_theme)

    def _create_passwords_tab(self) -> QWidget:
        """Создание вкладки со списком паролей."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(5)

        # Панель поиска и фильтров
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.search_input.textChanged.connect(self.filter_passwords)
        search_layout.addWidget(self.search_input)

        self.category_combo = QLineEdit()  # упрощённо, можно сделать комбобокс с категориями
        self.category_combo.setPlaceholderText("Категория (необязательно)")
        self.category_combo.textChanged.connect(self.filter_passwords)
        search_layout.addWidget(self.category_combo)

        layout.addLayout(search_layout)

        # Таблица паролей
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Название", "Логин", "URL", "Категория", "Действия"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.doubleClicked.connect(self._edit_password_from_table)
        layout.addWidget(self.table)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Добавить")
        add_btn.clicked.connect(self._add_password)
        btn_layout.addWidget(add_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(self._delete_selected)
        btn_layout.addWidget(delete_btn)

        export_btn = QPushButton("Экспорт")
        export_btn.clicked.connect(self._export_passwords)
        btn_layout.addWidget(export_btn)

        import_btn = QPushButton("Импорт")
        import_btn.clicked.connect(self._import_passwords)
        btn_layout.addWidget(import_btn)

        layout.addLayout(btn_layout)

        return tab

    def _create_generator_tab(self) -> QWidget:
        """Вкладка генератора паролей."""
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QCheckBox, QPushButton, QLineEdit

        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        # Длина
        len_layout = QHBoxLayout()
        len_layout.addWidget(QLabel("Длина:"))
        self.length_spin = QSpinBox()
        self.length_spin.setRange(4, 128)
        self.length_spin.setValue(16)
        len_layout.addWidget(self.length_spin)
        len_layout.addStretch()
        layout.addLayout(len_layout)

        # Опции
        self.lower_check = QCheckBox("Строчные (a-z)")
        self.lower_check.setChecked(True)
        layout.addWidget(self.lower_check)

        self.upper_check = QCheckBox("Заглавные (A-Z)")
        self.upper_check.setChecked(True)
        layout.addWidget(self.upper_check)

        self.digits_check = QCheckBox("Цифры (0-9)")
        self.digits_check.setChecked(True)
        layout.addWidget(self.digits_check)

        self.symbols_check = QCheckBox("Спецсимволы (!@#$%^&*)")
        self.symbols_check.setChecked(True)
        layout.addWidget(self.symbols_check)

        # Генерация
        gen_btn = QPushButton("Сгенерировать")
        gen_btn.clicked.connect(self._generate_password)
        layout.addWidget(gen_btn)

        # Результат
        self.result_edit = QLineEdit()
        self.result_edit.setReadOnly(True)
        self.result_edit.setPlaceholderText("Сгенерированный пароль")
        layout.addWidget(self.result_edit)

        # Кнопка копирования
        copy_btn = QPushButton("Копировать в буфер")
        copy_btn.clicked.connect(self._copy_generated)
        layout.addWidget(copy_btn)

        layout.addStretch()
        return tab

    def _create_tools_tab(self) -> QWidget:
        """Вкладка с дополнительными инструментами."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Сканер портов
        scanner = NetworkScannerWidget()
        layout.addWidget(scanner)

        # Можно добавить другие инструменты
        layout.addStretch()
        return tab

    def _create_toolbar(self) -> None:
        """Создание панели инструментов."""
        toolbar = QToolBar("Основная")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Действия
        add_action = QAction("Добавить", self)
        add_action.triggered.connect(self._add_password)
        toolbar.addAction(add_action)

        delete_action = QAction("Удалить", self)
        delete_action.triggered.connect(self._delete_selected)
        toolbar.addAction(delete_action)

        toolbar.addSeparator()

        export_action = QAction("Экспорт", self)
        export_action.triggered.connect(self._export_passwords)
        toolbar.addAction(export_action)

        import_action = QAction("Импорт", self)
        import_action.triggered.connect(self._import_passwords)
        toolbar.addAction(import_action)

        toolbar.addSeparator()

        settings_action = QAction("Настройки", self)
        settings_action.triggered.connect(self._show_settings)
        toolbar.addAction(settings_action)

        # Переключение темы (пока просто кнопка)
        theme_action = QAction("Сменить тему", self)
        theme_action.triggered.connect(self._toggle_theme)
        toolbar.addAction(theme_action)

    def _load_passwords(self) -> None:
        """Загрузка всех паролей в таблицу."""
        try:
            entries = self.password_manager.get_all_entries()
            self._populate_table(entries)
        except Exception as e:
            logger.error(f"Ошибка загрузки паролей: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить пароли:\n{e}")

    def _populate_table(self, entries: list) -> None:
        """Заполнение таблицы записями."""
        self.table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            # ID храним в data
            self.table.setItem(row, 0, QTableWidgetItem(entry.title))
            self.table.setItem(row, 1, QTableWidgetItem(entry.username or ""))
            self.table.setItem(row, 2, QTableWidgetItem(entry.url or ""))
            self.table.setItem(row, 3, QTableWidgetItem(entry.category or ""))
            # Действия - кнопка просмотра пароля
            view_btn = QPushButton("Показать")
            view_btn.clicked.connect(lambda checked, r=row: self._show_password(r))
            self.table.setCellWidget(row, 4, view_btn)
            # Сохраняем ID
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, entry.id)

    def filter_passwords(self) -> None:
        """Фильтрация по поиску и категории."""
        search = self.search_input.text().strip().lower()
        category = self.category_combo.text().strip().lower()
        if not search and not category:
            self._load_passwords()
            return
        try:
            entries = self.password_manager.search_entries(search, category)
            self._populate_table(entries)
        except Exception as e:
            logger.error(f"Ошибка фильтрации: {e}")

    def _add_password(self) -> None:
        """Открытие диалога добавления пароля."""
        dialog = PasswordDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.password_manager.add_entry(**data)
                self._load_passwords()
                self.statusBar().showMessage("Пароль добавлен")
            except Exception as e:
                logger.error(f"Ошибка добавления: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить запись:\n{e}")

    def _edit_password_from_table(self, index) -> None:
        """Редактирование по двойному клику."""
        row = index.row()
        item = self.table.item(row, 0)
        if not item:
            return
        entry_id = item.data(Qt.ItemDataRole.UserRole)
        if not entry_id:
            return
        entry = self.password_manager.get_entry_by_id(entry_id)
        if not entry:
            return
        dialog = PasswordDialog(self, entry)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.password_manager.update_entry(entry_id, **data)
                self._load_passwords()
                self.statusBar().showMessage("Запись обновлена")
            except Exception as e:
                logger.error(f"Ошибка обновления: {e}")
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить запись:\n{e}")

    def _delete_selected(self) -> None:
        """Удаление выбранных записей."""
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.information(self, "Информация", "Выберите записи для удаления.")
            return
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить {len(selected)} записей?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        ids = []
        for idx in selected:
            row = idx.row()
            item = self.table.item(row, 0)
            if item:
                entry_id = item.data(Qt.ItemDataRole.UserRole)
                if entry_id:
                    ids.append(entry_id)
        try:
            self.password_manager.delete_entries(ids)
            self._load_passwords()
            self.statusBar().showMessage(f"Удалено {len(ids)} записей")
        except Exception as e:
            logger.error(f"Ошибка удаления: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить записи:\n{e}")

    def _show_password(self, row: int) -> None:
        """Показать пароль для записи."""
        item = self.table.item(row, 0)
        if not item:
            return
        entry_id = item.data(Qt.ItemDataRole.UserRole)
        if not entry_id:
            return
        entry = self.password_manager.get_entry_by_id(entry_id)
        if not entry:
            return
        # Расшифровываем пароль
        try:
            password = self.password_manager.get_decrypted_password(entry_id)
            QMessageBox.information(
                self, "Пароль",
                f"Запись: {entry.title}\nПароль: {password}"
            )
        except Exception as e:
            logger.error(f"Ошибка расшифровки: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось показать пароль:\n{e}")

    def _show_context_menu(self, pos) -> None:
        """Контекстное меню для таблицы."""
        menu = QMenu()
        edit_action = menu.addAction("Редактировать")
        delete_action = menu.addAction("Удалить")
        copy_action = menu.addAction("Копировать пароль")
        action = menu.exec(self.table.mapToGlobal(pos))
        if action == edit_action:
            self._edit_password_from_table(self.table.currentIndex())
        elif action == delete_action:
            self._delete_selected()
        elif action == copy_action:
            self._copy_password()

    def _copy_password(self) -> None:
        """Копировать пароль выбранной записи в буфер."""
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if not item:
            return
        entry_id = item.data(Qt.ItemDataRole.UserRole)
        if not entry_id:
            return
        try:
            password = self.password_manager.get_decrypted_password(entry_id)
            QApplication.clipboard().setText(password)
            self.statusBar().showMessage("Пароль скопирован")
        except Exception as e:
            logger.error(f"Ошибка копирования: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось скопировать пароль:\n{e}")

    def _generate_password(self) -> None:
        """Генерация пароля по настройкам."""
        length = self.length_spin.value()
        use_lower = self.lower_check.isChecked()
        use_upper = self.upper_check.isChecked()
        use_digits = self.digits_check.isChecked()
        use_symbols = self.symbols_check.isChecked()
        try:
            password = generate_password(length, use_lower, use_upper, use_digits, use_symbols)
            self.result_edit.setText(password)
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def _copy_generated(self) -> None:
        """Копировать сгенерированный пароль."""
        text = self.result_edit.text()
        if text:
            QApplication.clipboard().setText(text)
            self.statusBar().showMessage("Пароль скопирован")

    def _export_passwords(self) -> None:
        """Экспорт паролей в файл."""
        from PyQt6.QtWidgets import QFileDialog
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Экспорт паролей",
            "passwords.json",
            "JSON (*.json);;CSV (*.csv);;Excel (*.xlsx);;YAML (*.yaml)"
        )
        if not file_path:
            return
        try:
            # Определяем формат по расширению или фильтру
            if file_path.endswith('.json'):
                self.import_export.export_json(file_path)
            elif file_path.endswith('.csv'):
                self.import_export.export_csv(file_path)
            elif file_path.endswith('.xlsx'):
                self.import_export.export_excel(file_path)
            elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
                self.import_export.export_yaml(file_path)
            else:
                # По умолчанию JSON
                self.import_export.export_json(file_path)
            self.statusBar().showMessage(f"Экспортировано в {file_path}")
        except Exception as e:
            logger.error(f"Ошибка экспорта: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось экспортировать:\n{e}")

    def _import_passwords(self) -> None:
        """Импорт паролей из файла."""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Импорт паролей",
            "",
            "JSON (*.json);;CSV (*.csv);;Excel (*.xlsx);;YAML (*.yaml)"
        )
        if not file_path:
            return
        try:
            if file_path.endswith('.json'):
                imported = self.import_export.import_json(file_path)
            elif file_path.endswith('.csv'):
                imported = self.import_export.import_csv(file_path)
            elif file_path.endswith('.xlsx'):
                imported = self.import_export.import_excel(file_path)
            elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
                imported = self.import_export.import_yaml(file_path)
            else:
                raise ValueError("Неподдерживаемый формат")
            self._load_passwords()
            self.statusBar().showMessage(f"Импортировано {imported} записей")
        except Exception as e:
            logger.error(f"Ошибка импорта: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось импортировать:\n{e}")

    def _show_settings(self) -> None:
        """Открытие диалога настроек."""
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Применяем изменения
            theme = dialog.get_theme()
            if theme != self.current_theme:
                self.current_theme = theme
                self.apply_theme(theme)

    def apply_theme(self, theme: str) -> None:
        """Применение темы ко всему приложению."""
        from pathlib import Path
        style_path = Path(__file__).parent / "resources" / "styles" / f"{theme}.qss"
        if style_path.exists():
            with open(style_path, "r", encoding="utf-8") as f:
                QApplication.instance().setStyleSheet(f.read())
        # Сохраняем настройку
        QSettings().setValue("theme", theme)

    def _toggle_theme(self) -> None:
        """Переключение между тёмной и светлой темой."""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme(new_theme)
        self.current_theme = new_theme
