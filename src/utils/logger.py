# -*- coding: utf-8 -*-

"""
Настройка логирования.
"""

import logging
import sys
from pathlib import Path

def setup_logging(log_file_path: Path) -> None:
    """Настройка логирования в файл и консоль."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
