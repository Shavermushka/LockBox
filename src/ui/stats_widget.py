# -*- coding: utf-8 -*-

"""
Виджет статистики с графиками.
"""

import logging
from typing import Optional

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

try:
    import matplotlib
    matplotlib.use('QtAgg')
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
except ImportError:
    FigureCanvas = None
    Figure = None

from src.logic.password_manager import PasswordManager

logger = logging.getLogger(__name__)

class StatsWidget(QWidget):
    """Виджет для отображения статистики."""

    def __init__(self, password_manager: PasswordManager) -> None:
        super().__init__()
        self.pm = password_manager
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        if FigureCanvas is None:
            layout.addWidget(QLabel("Для графиков установите matplotlib"))
            return

        # Создаём холст
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Кнопка обновления (можно добавить)
        from PyQt6.QtWidgets import QPushButton
        refresh_btn = QPushButton("Обновить статистику")
        refresh_btn.clicked.connect(self.update_stats)
        layout.addWidget(refresh_btn)

        self.update_stats()

    def update_stats(self) -> None:
        """Обновить графики."""
        if Figure is None:
            return
        try:
            entries = self.pm.get_all_entries()
            total = len(entries)
            categories = {}
            for e in entries:
                cat = e.category or "Без категории"
                categories[cat] = categories.get(cat, 0) + 1

            self.figure.clear()
            ax = self.figure.add_subplot(111)
            if categories:
                ax.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%')
                ax.set_title(f"Всего записей: {total}")
            else:
                ax.text(0.5, 0.5, "Нет данных", ha='center', va='center')
                ax.set_title("Статистика")
            self.canvas.draw()
        except Exception as e:
            logger.error(f"Ошибка обновления статистики: {e}")
