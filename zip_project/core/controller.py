# core/controller.py
import logging
from pathlib import Path

from ..config.model import ConfigModel
from ..config.resolver import ConfigResolver
from .scanner import Scanner
from .manifest_writer import ManifestWriter
from .archiver import Archiver

logger = logging.getLogger(__name__)

class Controller:
    def __init__(self, config: ConfigModel, config_dir: Path):
        self.config = config
        self.config_dir = config_dir

    def run(self):
        # Разрешение путей (может быть вынесено в отдельный шаг)
        resolver = ConfigResolver(self.config_dir)
        resolved_config = resolver.resolve(self.config)

        # Сканирование
        scanner = Scanner(resolved_config)
        files = scanner.scan()
        logger.info(f"Found {len(files)} files")

        # Сухой запуск
        if resolved_config.dry_run:
            print("Dry run - files to be processed:")
            for f in sorted(files):
                print(f"  {f}")
            return

        # Запись манифеста
        output_manifest = self._resolve_output_path(resolved_config.manifest.file)
        writer = ManifestWriter(resolved_config, resolved_config.resolved_base_dirs)
        writer.write(files, output_manifest)

        # Архивация
        if resolved_config.archive.enabled and files:
            output_archive = self._resolve_output_path(resolved_config.archive.file)
            archiver = Archiver(resolved_config, resolved_config.resolved_base_dirs)
            archiver.archive(files, output_archive)
        elif resolved_config.archive.enabled:
            logger.warning("No files to archive")

    def _resolve_output_path(self, path_str: str) -> Path:
        p = Path(path_str).expanduser()
        return p if p.is_absolute() else (self.config_dir / p)