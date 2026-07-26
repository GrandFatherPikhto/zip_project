# config/loader.py
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
import yaml
from argparse import Namespace

from .defaults import DEFAULT_CONFIG
from .model import ConfigModel

class ConfigLoader:
    def __init__(self, cli_args: Optional[Namespace] = None):
        self.cli_args = cli_args or Namespace()
        self.config_path: Optional[Path] = None

    def _find_config_path(self, provided_path: Optional[str] = None) -> Path:
        """Определяет путь к конфигу в порядке: аргумент -> рядом с exe -> cwd -> создаёт в cwd."""
        if provided_path:
            return Path(provided_path).absolute()

        # Путь к исполняемому файлу (или скрипту)
        if getattr(sys, 'frozen', False):
            script_dir = Path(sys.executable).parent
        else:
            script_dir = Path(__file__).parent.parent  # корень проекта

        # Ищем в папке exe, затем в cwd
        candidates = [
            script_dir / "zip_project.yaml",
            Path.cwd() / "zip_project.yaml"
        ]
        for cand in candidates:
            if cand.exists():
                return cand

        # Если нет – создаём в cwd
        default_path = Path.cwd() / "zip_project.yaml"
        return default_path

    def _expand_env_vars(self, data: Any) -> Any:
        """Рекурсивно заменяет ${VAR} на переменные окружения."""
        if isinstance(data, dict):
            return {k: self._expand_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._expand_env_vars(item) for item in data]
        elif isinstance(data, str):
            # Заменяем ${VAR} или $VAR
            import re
            def repl(match):
                var = match.group(1) or match.group(2)
                return os.environ.get(var, match.group(0))
            return re.sub(r'\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)', repl, data)
        else:
            return data

    def _merge_cli_overrides(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Переопределяет ключи конфига из аргументов командной строки."""
        cli = self.cli_args
        overrides = {}
        if hasattr(cli, 'base_dir') and cli.base_dir is not None:
            overrides['base_working_dir'] = cli.base_dir
        if hasattr(cli, 'include_dir') and cli.include_dir:
            # Если переданы --include-dir, добавляем к scan_dirs (не заменяем)
            existing = config_dict.get('scan_dirs', [])
            if isinstance(existing, list):
                existing.extend(cli.include_dir)
                overrides['scan_dirs'] = existing
            else:
                overrides['scan_dirs'] = cli.include_dir
        if hasattr(cli, 'exclude') and cli.exclude:
            existing = config_dict.get('exclude_patterns', [])
            if isinstance(existing, list):
                existing.extend(cli.exclude)
                overrides['exclude_patterns'] = existing
            else:
                overrides['exclude_patterns'] = cli.exclude
        if hasattr(cli, 'output') and cli.output is not None:
            overrides['manifest'] = config_dict.get('manifest', {})
            overrides['manifest']['file'] = cli.output
        if hasattr(cli, 'zip') and cli.zip is not None:
            overrides['archive'] = config_dict.get('archive', {})
            overrides['archive']['enabled'] = cli.zip
        if hasattr(cli, 'dry_run') and cli.dry_run is not None:
            overrides['dry_run'] = cli.dry_run
        # Можно добавить другие переопределения
        return {**config_dict, **overrides}

    def load(self, config_path: Optional[str] = None) -> ConfigModel:
        # 1. Найти конфиг
        self.config_path = self._find_config_path(config_path)
        raw_config = {}

        # 2. Если конфиг существует – читаем
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    raw_config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"[Ошибка] Не удалось прочитать конфиг: {e}")
                # Продолжаем с дефолтами

        # 3. Подстановка переменных окружения
        raw_config = self._expand_env_vars(raw_config)

        # 4. Слияние с дефолтами (глубокое слияние)
        merged = self._deep_merge(DEFAULT_CONFIG, raw_config)

        # 5. Переопределения из CLI
        merged = self._merge_cli_overrides(merged)

        # 6. Создание модели (валидация)
        try:
            model = ConfigModel(**merged)
        except Exception as e:
            print(f"[Ошибка] Некорректная конфигурация: {e}")
            sys.exit(1)

        # Сохраняем путь к конфигу в модели (можно добавить поле)
        model._config_path = self.config_path  # не входит в схему, но можно использовать
        return model

    @staticmethod
    def _deep_merge(base: Dict, override: Dict) -> Dict:
        """Рекурсивное слияние двух словарей."""
        result = base.copy()
        for key, val in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(val, dict):
                result[key] = ConfigLoader._deep_merge(result[key], val)
            else:
                result[key] = val
        return result