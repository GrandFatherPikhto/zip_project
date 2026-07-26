# core/scanner.py
import os
import time
from pathlib import Path
from typing import Set, List, Optional
import logging

from ..utils.glob_utils import matches_any
from ..config.model import ConfigModel

logger = logging.getLogger(__name__)

class Scanner:
    def __init__(self, config: ConfigModel):
        self.config = config
        self.base_dirs = config.resolved_base_dirs
        self.scan_dirs = config.resolved_scan_dirs
        self.exclude_patterns = config.exclude_patterns
        self.exclude_extensions = set(config.exclude_extensions)
        self.extensions = set(config.extensions)
        self.max_size_mb = config.max_file_size_mb
        self.min_age_days = config.min_file_age_days
        self.encoding = config.encoding
        self.single_files = [Path(f) for f in config.single_files]  # относительные, будут разрешены позже

    def scan(self) -> Set[Path]:
        found = set()

        # Добавляем одиночные файлы (если существуют)
        for base in self.base_dirs:
            for sf in self.single_files:
                abs_path = base / sf
                if abs_path.is_file():
                    if self._include_file(abs_path):
                        found.add(abs_path)
                else:
                    logger.debug(f"Single file not found: {abs_path}")

        # Обходим каталоги, перечисленные в scan_dirs (относительно своего base)
        for base, scan_dir in self.scan_dirs:
            if not scan_dir.exists():
                logger.warning(f"Scan directory not found: {scan_dir}")
                continue
            # Рекурсивный обход
            for root, dirs, files in os.walk(scan_dir):
                root_path = Path(root)
                # Исключаем папки, соответствующие паттернам
                # Проверяем относительный путь от базы
                rel_root = root_path.relative_to(base)
                # Если rel_root соответствует любому исключающему паттерну – пропускаем всю папку
                if self._is_excluded(rel_root):
                    # Удаляем из списка обхода, чтобы не заходить внутрь
                    dirs.clear()
                    continue

                # Фильтруем подпапки для дальнейшего обхода (чтобы не заходить в исключённые)
                filtered_dirs = []
                for d in dirs:
                    rel_dir = rel_root / d
                    if not self._is_excluded(rel_dir):
                        filtered_dirs.append(d)
                dirs[:] = filtered_dirs

                # Обрабатываем файлы
                for file in files:
                    file_path = root_path / file
                    rel_file = rel_root / file
                    if self._is_excluded(rel_file):
                        continue
                    if self._include_file(file_path):
                        found.add(file_path)

        return found

    def _is_excluded(self, rel_path: Path) -> bool:
        """Проверяет, соответствует ли относительный путь паттерну исключения."""
        # Проверяем паттерны
        if matches_any(rel_path, self.exclude_patterns):
            return True
        # Проверяем расширение
        if rel_path.suffix.lower() in self.exclude_extensions:
            return True
        return False

    def _include_file(self, abs_path: Path) -> bool:
        """Проверяет, должен ли файл быть включён (расширение, размер, дата)."""
        # Расширение
        if self.extensions and abs_path.suffix.lower() not in self.extensions:
            return False
        # Размер
        if self.max_size_mb is not None:
            size_bytes = abs_path.stat().st_size
            if size_bytes > self.max_size_mb * 1024 * 1024:
                return False
        # Дата
        if self.min_age_days is not None:
            mtime = abs_path.stat().st_mtime
            age_days = (time.time() - mtime) / (24 * 3600)
            if age_days > self.min_age_days:
                return False
        return True