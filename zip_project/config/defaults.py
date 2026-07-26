# config/defaults.py
from typing import List, Dict, Any

DEFAULT_CONFIG: Dict[str, Any] = {
    "project_name": None,
    "base_working_dir": ".",
    "encoding": "utf-8",
    "dry_run": False,
    "scan_dirs": ["src", "modules"],
    "single_files": ["main.py", "config.py"],
    "extensions": [".py"],
    "exclude_patterns": [
        "**/__pycache__",
        "**/*.pyc",
        "**/.venv",
        "**/venv",
        "**/.git",
        "**/temp/*"
    ],
    "exclude_extensions": [".log", ".tmp"],
    "max_file_size_mb": None,
    "min_file_age_days": None,
    "manifest": {
        "file": "project_list.txt",
        "format": "plain",
        "include_metadata": False
    },
    "archive": {
        "enabled": False,
        "file": "archive.zip",
        "format": "zip",
        "compression_level": 6,
        "password": None
    }
}