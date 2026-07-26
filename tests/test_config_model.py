import pytest
from pydantic import ValidationError

from zip_project.config.model import ArchiveSettings, ConfigModel, ManifestSettings


def test_extensions_get_dot_prefix_when_missing():
    cfg = ConfigModel(extensions=["py", ".md"], exclude_extensions=["log"])
    assert cfg.extensions == [".py", ".md"]
    assert cfg.exclude_extensions == [".log"]


def test_scan_dirs_and_single_files_both_empty_is_invalid():
    with pytest.raises(ValidationError):
        ConfigModel(scan_dirs=[], single_files=[])


def test_scan_dirs_empty_ok_if_single_files_present():
    cfg = ConfigModel(scan_dirs=[], single_files=["main.py"])
    assert cfg.scan_dirs == []


def test_manifest_file_cannot_be_empty():
    with pytest.raises(ValidationError):
        ManifestSettings(file="  ")


def test_archive_file_cannot_be_empty():
    with pytest.raises(ValidationError):
        ArchiveSettings(file="")


def test_defaults_are_sane():
    cfg = ConfigModel()
    assert cfg.archive.enabled is False
    assert cfg.manifest.format == "plain"
    assert cfg.resolved_base_dirs == []
    assert cfg.resolved_scan_dirs == []
