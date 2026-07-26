# utils/glob_utils.py
import fnmatch
from pathlib import Path
import re

# utils/glob_utils.py
import fnmatch
from pathlib import Path


def path_matches_pattern(path: Path, pattern: str) -> bool:
    """
    Проверяет, соответствует ли относительный путь glob-паттерну,
    поддерживающему ** (рекурсивное сопоставление).
    """
    # Разбиваем путь на сегменты
    path_parts = path.parts  # кортеж, например ('.venv', 'Lib', ...)
    # Разбиваем паттерн по '/', убираем пустые
    pattern_parts = [p for p in pattern.split('/') if p != '']

    # Рекурсивное сопоставление
    def match(p_i: int, pp_i: int) -> bool:
        # Если оба закончились – успех
        if p_i == len(path_parts) and pp_i == len(pattern_parts):
            return True
        # Если паттерн закончился, а путь нет – неудача
        if pp_i == len(pattern_parts):
            return False

        # Если текущий сегмент паттерна — **
        if pattern_parts[pp_i] == '**':
            # Вариант 1: пропустить ** (съесть 0 сегментов)
            if match(p_i, pp_i + 1):
                return True
            # Вариант 2: съесть один сегмент пути и остаться на том же **
            if p_i < len(path_parts) and match(p_i + 1, pp_i):
                return True
            return False

        # Обычный сегмент
        if p_i >= len(path_parts):
            return False

        seg_pattern = pattern_parts[pp_i]
        # Сравниваем сегмент пути с шаблоном (поддерживается * и ?)
        if fnmatch.fnmatch(path_parts[p_i], seg_pattern):
            return match(p_i + 1, pp_i + 1)
        return False

    return match(0, 0)


def matches_any(path: Path, patterns: list) -> bool:
    """Проверяет, соответствует ли путь хотя бы одному паттерну."""
    for pat in patterns:
        if path_matches_pattern(path, pat):
            return True
    return False
