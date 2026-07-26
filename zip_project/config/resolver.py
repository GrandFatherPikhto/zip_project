# config/resolver.py
import os
from pathlib import Path
from typing import List, Set, Tuple, Optional
import fnmatch

from .model import ConfigModel

class ConfigResolver:
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir

    def resolve(self, config: ConfigModel) -> ConfigModel:
        # Клонируем (или создаём новую модель)
        # Преобразуем base_working_dir в список абсолютных путей
        base_dirs = config.base_working_dir
        if isinstance(base_dirs, str):
            base_dirs = [base_dirs]

        resolved_bases: List[Path] = []
        for bd in base_dirs:
            if not bd.strip():
                bd = "."
            abs_path = self._resolve_path(bd)
            resolved_bases.append(abs_path)

        config.resolved_base_dirs = resolved_bases

        # Разворачиваем scan_dirs относительно каждого base_working_dir.
        # Храним пары (base, scan_dir), чтобы сканер мог считать относительные
        # пути (для exclude_patterns) от base, а обходить только scan_dir.
        resolved_scan_dirs: List[Tuple[Path, Path]] = []
        for base in resolved_bases:
            for sd in config.scan_dirs:
                sd = sd.strip() if isinstance(sd, str) else sd
                if not sd:
                    sd = "."
                scan_path = (base / sd).resolve()
                resolved_scan_dirs.append((base, scan_path))

        config.resolved_scan_dirs = resolved_scan_dirs

        # Можно также предварительно скомпилировать exclude_patterns в регулярки для скорости,
        # но оставим как есть, сканер будет использовать fnmatch.
        return config

    def _resolve_path(self, path_str: str) -> Path:
        """Преобразует относительный путь в абсолютный относительно config_dir."""
        p = Path(path_str).expanduser()
        if p.is_absolute():
            return p.resolve()
        else:
            return (self.config_dir / p).resolve()

    @staticmethod
    def match_any_pattern(path: Path, patterns: List[str]) -> bool:
        """Проверяет, соответствует ли путь (строковое представление) одному из glob-паттернов."""
        path_str = str(path).replace("\\", "/")  # для кроссплатформенности
        for pat in patterns:
            # Преобразуем паттерн в формат fnmatch (с поддержкой **)
            # Простая эмуляция ** как рекурсивного обхода – в fnmatch нет **, 
            # поэтому мы будем использовать пользовательскую логику в сканере.
            # Здесь оставляем как есть, а сканер будет проверять вхождение.
            if fnmatch.fnmatch(path_str, pat):
                return True
            # Дополнительно проверяем вхождение паттерна в путь (если паттерн содержит * и т.д.)
            # Можно использовать более сложную логику, но для простоты пока так.
        return False