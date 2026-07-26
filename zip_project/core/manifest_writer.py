# core/manifest_writer.py
import json
import csv
from pathlib import Path
from typing import Set, List, Dict
import logging

from ..config.model import ConfigModel

logger = logging.getLogger(__name__)

class ManifestWriter:
    def __init__(self, config: ConfigModel, base_dirs: List[Path]):
        self.config = config
        self.base_dirs = base_dirs

    def write(self, files: Set[Path], output_path: Path):
        # Сортируем для стабильности
        sorted_files = sorted(files)
        # Получаем относительные пути (от первого base_dir, но можно выбрать)
        # Для простоты используем первый base_dir как главный, но можно определить общий префикс.
        # Если файлы находятся в разных base_dirs, то относительный путь будет от общего корня.
        # Мы будем использовать os.path.relpath относительно первого base_dir, но если файл вне его, то будет ../..
        # Это не идеально, но оставим для простоты.
        main_base = self.base_dirs[0] if self.base_dirs else Path.cwd()
        entries = []
        for f in sorted_files:
            rel = f.relative_to(main_base) if f.is_relative_to(main_base) else f
            if self.config.manifest.include_metadata:
                stat = f.stat()
                entries.append({
                    "path": str(rel),
                    "size": stat.st_size,
                    "mtime": stat.st_mtime
                })
            else:
                entries.append(str(rel))

        # Определяем формат
        fmt = self.config.manifest.format
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if fmt == "plain":
            with open(output_path, 'w', encoding=self.config.encoding) as f:
                for entry in entries:
                    if isinstance(entry, dict):
                        f.write(entry["path"] + "\n")
                    else:
                        f.write(entry + "\n")
        elif fmt == "json":
            with open(output_path, 'w', encoding=self.config.encoding) as f:
                json.dump(entries, f, indent=2, ensure_ascii=False)
        elif fmt == "csv":
            with open(output_path, 'w', newline='', encoding=self.config.encoding) as f:
                if self.config.manifest.include_metadata:
                    writer = csv.DictWriter(f, fieldnames=["path", "size", "mtime"])
                    writer.writeheader()
                    writer.writerows(entries)
                else:
                    writer = csv.writer(f)
                    writer.writerow(["path"])
                    for e in entries:
                        writer.writerow([e])
        else:
            raise ValueError(f"Unsupported manifest format: {fmt}")

        logger.info(f"Manifest written to {output_path}")