import tarfile
import zipfile
from pathlib import Path

from zip_project.config.model import ConfigModel
from zip_project.core.archiver import Archiver


def _files(tmp_path):
    (tmp_path / "a.py").write_text("a")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.py").write_text("b")
    return {tmp_path / "a.py", tmp_path / "sub" / "b.py"}


def test_zip_archive_contains_relative_arcnames(tmp_path):
    files = _files(tmp_path)
    cfg = ConfigModel(archive={"enabled": True, "file": "out.zip", "format": "zip"})
    out = tmp_path / "out.zip"

    Archiver(cfg, [tmp_path]).archive(files, out)

    with zipfile.ZipFile(out) as zf:
        names = set(zf.namelist())
    assert names == {"a.py", str(Path("sub") / "b.py").replace("\\", "/")}


def test_tar_gz_archive_contains_relative_arcnames(tmp_path):
    files = _files(tmp_path)
    cfg = ConfigModel(archive={"enabled": True, "file": "out.tar.gz", "format": "tar.gz"})
    out = tmp_path / "out.tar.gz"

    Archiver(cfg, [tmp_path]).archive(files, out)

    with tarfile.open(out) as tf:
        names = set(tf.getnames())
    assert names == {"a.py", str(Path("sub") / "b.py").replace("\\", "/")}


def test_archive_creates_missing_parent_dirs(tmp_path):
    files = _files(tmp_path)
    cfg = ConfigModel(archive={"enabled": True, "file": "nested/out.zip", "format": "zip"})
    out = tmp_path / "nested" / "out.zip"

    Archiver(cfg, [tmp_path]).archive(files, out)

    assert out.exists()
