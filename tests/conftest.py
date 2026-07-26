import sys
from pathlib import Path

# Гарантируем, что пакет zip_project импортируется независимо от того,
# как запущен pytest (python -m pytest vs pytest).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
