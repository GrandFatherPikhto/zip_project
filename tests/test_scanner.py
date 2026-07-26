from pathlib import Path

from zip_project.config.model import ConfigModel
from zip_project.config.resolver import ConfigResolver
from zip_project.core.scanner import Scanner


def _make_project(tmp_path: Path) -> Path:
    (tmp_path / "a.py").write_text("print('a')")
    (tmp_path / "notes.txt").write_text("not included")
    (tmp_path / "single.py").write_text("print('single')")

    pycache = tmp_path / "__pycache__"
    pycache.mkdir()
    (pycache / "a.cpython-312.pyc").write_text("cached")

    old = tmp_path / "old"
    old.mkdir()
    (old / "legacy.py").write_text("print('legacy')")

    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.py").write_text("print('c')")

    return tmp_path


def _scan(tmp_path, **overrides):
    defaults = dict(
        base_working_dir=".",
        scan_dirs=["."],
        single_files=[],
        extensions=[".py"],
        exclude_patterns=["**/__pycache__", "**/old"],
    )
    defaults.update(overrides)
    cfg = ConfigModel(**defaults)
    resolved = ConfigResolver(tmp_path).resolve(cfg)
    return Scanner(resolved).scan()


def test_scan_finds_py_files_and_respects_extension_filter(tmp_path):
    _make_project(tmp_path)
    found = _scan(tmp_path)
    rel = {p.relative_to(tmp_path) for p in found}

    assert Path("a.py") in rel
    assert Path("sub/c.py") in rel
    assert Path("notes.txt") not in rel


def test_scan_excludes_patterns_recursively(tmp_path):
    _make_project(tmp_path)
    found = _scan(tmp_path)
    rel = {p.relative_to(tmp_path) for p in found}

    assert not any(p.parts[0] == "__pycache__" for p in rel)
    assert not any(p.parts[0] == "old" for p in rel)


def test_scan_dirs_restricts_which_subtrees_are_walked(tmp_path):
    _make_project(tmp_path)

    # Раньше scan_dirs игнорировался и сканировался весь base_working_dir.
    # Сузив scan_dirs до "sub", top-level a.py не должен попасть в результат.
    found = _scan(tmp_path, scan_dirs=["sub"])
    rel = {p.relative_to(tmp_path) for p in found}

    assert rel == {Path("sub/c.py")}


def test_scan_dirs_missing_directory_is_skipped_without_error(tmp_path):
    _make_project(tmp_path)
    found = _scan(tmp_path, scan_dirs=["does_not_exist"])
    assert found == set()


def test_single_files_included_even_outside_scan_dirs(tmp_path):
    _make_project(tmp_path)

    found = _scan(tmp_path, scan_dirs=["sub"], single_files=["single.py"])
    rel = {p.relative_to(tmp_path) for p in found}

    assert Path("single.py") in rel
    assert Path("sub/c.py") in rel


def test_max_file_size_filters_large_files(tmp_path):
    _make_project(tmp_path)
    big = tmp_path / "big.py"
    big.write_bytes(b"x" * (2 * 1024 * 1024))

    found = _scan(tmp_path, max_file_size_mb=1)
    rel = {p.relative_to(tmp_path) for p in found}

    assert Path("big.py") not in rel
    assert Path("a.py") in rel
