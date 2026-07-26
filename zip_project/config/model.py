# config/model.py
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Tuple, Union, Literal
from pathlib import Path


class ManifestSettings(BaseModel):
    file: str = "project_list.txt"
    format: Literal["plain", "json", "csv"] = "plain"
    include_metadata: bool = False

    @field_validator("file")
    @classmethod
    def file_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("manifest.file cannot be empty")
        return v


class ArchiveSettings(BaseModel):
    enabled: bool = False
    file: str = "archive.zip"
    format: Literal["zip", "tar.gz"] = "zip"
    compression_level: int = Field(6, ge=0, le=9)
    password: Optional[str] = None

    @field_validator("file")
    @classmethod
    def file_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("archive.file cannot be empty")
        return v


class ConfigModel(BaseModel):
    # Общие
    project_name: Optional[str] = None
    base_working_dir: Union[str, List[str]] = "."
    encoding: str = "utf-8"
    dry_run: bool = False

    # Сканирование
    scan_dirs: List[str] = Field(default_factory=lambda: ["src", "modules"])
    single_files: List[str] = Field(default_factory=lambda: ["main.py", "config.py"])
    extensions: List[str] = Field(default_factory=lambda: [".py"])

    # Исключения
    exclude_patterns: List[str] = Field(default_factory=lambda: [
        "**/__pycache__", "**/*.pyc", "**/.venv", "**/venv", "**/.git", "**/temp/*"
    ])
    exclude_extensions: List[str] = Field(default_factory=lambda: [".log", ".tmp"])

    # Ограничения
    max_file_size_mb: Optional[int] = None
    min_file_age_days: Optional[int] = None   # 0 = только сегодня

    # Выходные данные
    manifest: ManifestSettings = Field(default_factory=ManifestSettings)
    archive: ArchiveSettings = Field(default_factory=ArchiveSettings)

    # Внутренние поля (заполняются после разрешения, не из YAML)
    resolved_base_dirs: List[Path] = Field(default_factory=list, exclude=True)
    resolved_scan_dirs: List[Tuple[Path, Path]] = Field(default_factory=list, exclude=True)

    # --- Валидаторы ---

    @field_validator("extensions", "exclude_extensions", mode="before")
    @classmethod
    def ensure_dot_prefix(cls, v: Union[str, List[str]]) -> Union[str, List[str]]:
        """Добавляет точку перед расширением, если её нет."""
        if isinstance(v, str):
            return v if v.startswith(".") else "." + v
        if isinstance(v, list):
            return [item if item.startswith(".") else "." + item for item in v]
        return v

    @model_validator(mode="after")
    def validate_scan_dirs_not_empty(self) -> "ConfigModel":
        if not self.scan_dirs and not self.single_files:
            raise ValueError("At least one of scan_dirs or single_files must be non-empty")
        return self