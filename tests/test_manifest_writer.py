import csv
import json
from pathlib import Path

from zip_project.config.model import ConfigModel
from zip_project.core.manifest_writer import ManifestWriter


def _files(tmp_path):
    (tmp_path / "a.py").write_text("a")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.py").write_text("b")
    return {tmp_path / "a.py", tmp_path / "sub" / "b.py"}


def test_plain_manifest_lists_relative_paths_sorted(tmp_path):
    files = _files(tmp_path)
    cfg = ConfigModel()
    out = tmp_path / "manifest.txt"

    ManifestWriter(cfg, [tmp_path]).write(files, out)

    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines == ["a.py", str(Path("sub") / "b.py")]


def test_json_manifest_with_metadata(tmp_path):
    files = _files(tmp_path)
    cfg = ConfigModel(manifest={"file": "m.json", "format": "json", "include_metadata": True})
    out = tmp_path / "manifest.json"

    ManifestWriter(cfg, [tmp_path]).write(files, out)

    data = json.loads(out.read_text(encoding="utf-8"))
    assert {"path", "size", "mtime"} <= data[0].keys()
    assert {e["path"] for e in data} == {"a.py", str(Path("sub") / "b.py")}


def test_csv_manifest_without_metadata(tmp_path):
    files = _files(tmp_path)
    cfg = ConfigModel(manifest={"file": "m.csv", "format": "csv", "include_metadata": False})
    out = tmp_path / "manifest.csv"

    ManifestWriter(cfg, [tmp_path]).write(files, out)

    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["path"]
    assert {r[0] for r in rows[1:]} == {"a.py", str(Path("sub") / "b.py")}
