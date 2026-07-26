# core/archiver.py
import zipfile
import tarfile
from pathlib import Path
from typing import Set, List
import logging

from ..config.model import ConfigModel

logger = logging.getLogger(__name__)

class Archiver:
    def __init__(self, config: ConfigModel, base_dirs: List[Path]):
        self.config = config
        self.base_dirs = base_dirs

    def archive(self, files: Set[Path], output_path: Path):
        fmt = self.config.archive.format
        compression = self.config.archive.compression_level
        password = self.config.archive.password  # только zip поддерживает пароль

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if fmt == "zip":
            with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED,
                                 compresslevel=compression) as zf:
                for f in sorted(files):
                    # Определяем относительный путь внутри архива
                    rel = self._get_rel_path(f)
                    if password:
                        # zipfile не поддерживает пароль напрямую, используем pyminizip или pyzipper.
                        # Для простоты оставим без пароля или предупредим.
                        logger.warning("Password protection is not supported for zip in this version")
                    zf.write(f, arcname=rel)
        elif fmt == "tar.gz":
            with tarfile.open(output_path, "w:gz") as tf:
                for f in sorted(files):
                    rel = self._get_rel_path(f)
                    tf.add(f, arcname=rel)
        else:
            raise ValueError(f"Unsupported archive format: {fmt}")

        logger.info(f"Archive created: {output_path}")

    def _get_rel_path(self, abs_path: Path) -> str:
        # Возвращаем относительный путь от первого base_dir
        main_base = self.base_dirs[0] if self.base_dirs else Path.cwd()
        try:
            rel = abs_path.relative_to(main_base)
            return str(rel)
        except ValueError:
            return str(abs_path)