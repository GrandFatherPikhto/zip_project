from pathlib import Path

from zip_project.config.model import ConfigModel
from zip_project.config.resolver import ConfigResolver


def test_resolve_single_base_dir_and_scan_dirs(tmp_path):
    cfg = ConfigModel(
        base_working_dir=".",
        scan_dirs=["src", "docs"],
        single_files=[],
    )
    resolved = ConfigResolver(tmp_path).resolve(cfg)

    assert resolved.resolved_base_dirs == [tmp_path.resolve()]
    assert resolved.resolved_scan_dirs == [
        (tmp_path.resolve(), (tmp_path / "src").resolve()),
        (tmp_path.resolve(), (tmp_path / "docs").resolve()),
    ]


def test_resolve_dot_scan_dir_means_base_itself(tmp_path):
    cfg = ConfigModel(base_working_dir=".", scan_dirs=["."], single_files=[])
    resolved = ConfigResolver(tmp_path).resolve(cfg)

    assert resolved.resolved_scan_dirs == [(tmp_path.resolve(), tmp_path.resolve())]


def test_resolve_multiple_base_dirs_cross_product(tmp_path):
    base_a = tmp_path / "a"
    base_b = tmp_path / "b"
    base_a.mkdir()
    base_b.mkdir()

    cfg = ConfigModel(
        base_working_dir=[str(base_a), str(base_b)],
        scan_dirs=["sub1", "sub2"],
        single_files=[],
    )
    resolved = ConfigResolver(tmp_path).resolve(cfg)

    assert resolved.resolved_base_dirs == [base_a.resolve(), base_b.resolve()]
    assert resolved.resolved_scan_dirs == [
        (base_a.resolve(), (base_a / "sub1").resolve()),
        (base_a.resolve(), (base_a / "sub2").resolve()),
        (base_b.resolve(), (base_b / "sub1").resolve()),
        (base_b.resolve(), (base_b / "sub2").resolve()),
    ]


def test_relative_base_dir_resolved_against_config_dir(tmp_path):
    sub = tmp_path / "project"
    sub.mkdir()

    cfg = ConfigModel(base_working_dir="project", scan_dirs=["."], single_files=[])
    resolved = ConfigResolver(tmp_path).resolve(cfg)

    assert resolved.resolved_base_dirs == [sub.resolve()]
