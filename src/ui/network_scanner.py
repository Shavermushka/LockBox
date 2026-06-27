# -*- coding: utf-8 -*-

"""
Виджет для сканирования сети (портов).
"""

import logging
import socket
import threading
from typing import List, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QProgressBar
)
from PyQt6.QtCore import pyqtSignal, QObject, Qt

logger = logging.getLogger(__name__)

class ScannerWorker(QObject):
    """Рабочий поток для сканирования портов."""
    progress = pyqtSignal(int, int)  # текущий, всего
    result = pyqtSignal(int, int)    # порт, статус (1 открыт, 0 закрыт)
    finished = pyqtSignal()

    def __init__(self, host: str, ports: List[int], timeout: float = 1.0):
        super().__init__()
        self.host = host
        self.ports = ports
        self.timeout = timeout
        self._stop = False

    def stop(self) -> None:
        self._stop = True

    def run(self) -> None:
        total = len(self.ports)
        for i, port in enumerate(self.ports):
            if self._stop:
                break
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.timeout)
                result = sock.connect_ex((self.host, port))
                sock.close()
                status = 1 if result == 0 else 0
                self.result.emit(port, status)
            except Exception as e:
                logger.error(f"Ошибка сканирования порта {port}: {e}")
            self.progress.emit(i + 1, total)

        self.finished.emit()

class NetworkScannerWidget(QWidget):
    """Виджет сканера портов."""

    def __init__(self) -> None:
        super().__init__()
        self.worker: Optional[ScannerWorker] = None
        self.thread: Optional[threading.Thread] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Параметры
        top_layout = QHBoxLayout()
        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText("IP или хост (например, 192.168.0.1)")
        self.host_edit.setText("127.0.0.1")
        top_layout.addWidget(self.host_edit)

        self.port_range_edit = QLineEdit()
        self.port_range_edit.setPlaceholderText("Диапазон портов (например, 1-1024)")
        self.port_range_edit.setText("1-1024")
        top_layout.addWidget(self.port_range_edit)

        self.scan_btn = QPushButton("Сканировать")
        self.scan_btn.clicked.connect(self.start_scan)
        top_layout.addWidget(self.scan_btn)

        self.stop_btn = QPushButton("Остановить")
        self.stop_btn.clicked.connect(self.stop_scan)
        self.stop_btn.setEnabled(False)
        top_layout.addWidget(self.stop_btn)

        layout.addLayout(top_layout)

        # Прогресс
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Таблица результатов
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Порт", "Статус"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Статус
        self.status_label = QLabel("Готов")
        layout.addWidget(self.status_label)

    def start_scan(self) -> None:
        """Запуск сканирования."""
        host = self.host_edit.text().strip()
        if not host:
            self.status_label.setText("Введите хост")
            return
        port_text = self.port_range_edit.text().strip()
        if not port_text:
            self.status_label.setText("Введите диапазон портов")
            return

        try:
            if '-' in port_text:
                start, end = port_text.split('-')
                start = int(start.strip())
                end = int(end.strip())
                ports = list(range(start, end + 1))
            else:
                ports = [int(port_text)]
        except ValueError:
            self.status_label.setText("Неверный формат диапазона")
            return

        if not ports:
            return

        self.table.setRowCount(0)
        self.progress_bar.setMaximum(len(ports))
        self.progress_bar.setValue(0)
        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Сканирование...")

        # Запуск в потоке
        self.worker = ScannerWorker(host, ports, timeout=0.5)
        self.worker.progress.connect(self.update_progress)
        self.worker.result.connect(self.add_result)
        self.worker.finished.connect(self.scan_finished)

        self.thread = threading.Thread(target=self.worker.run)
        self.thread.start()

    def stop_scan(self) -> None:
        """Остановка сканирования."""
        if self.worker:
            self.worker.stop()
            self.status_label.setText("Остановка...")

    def update_progress(self, current: int, total: int) -> None:
        """Обновление прогресс-бара."""
        self.progress_bar.setValue(current)

    def add_result(self, port: int, status: int) -> None:
        """Добавление результата в таблицу."""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(port)))
        status_text = "Открыт" if status == 1 else "Закрыт"
        self.table.setItem(row, 1, QTableWidgetItem(status_text))
        if status == 1:
            self.table.item(row, 1).setBackground(Qt.GlobalColor.green)

    def scan_finished(self) -> None:
        """Завершение сканирования."""
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Сканирование завершено")
        self.progress_bar.setValue(self.progress_bar.maximum())
