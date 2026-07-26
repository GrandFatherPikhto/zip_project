from argparse import Namespace

import pytest

from zip_project.config.loader import ConfigLoader


def _cli(**over):
    base = dict(
        base_dir=None,
        include_dir=None,
        exclude=None,
        output=None,
        zip=None,
        dry_run=None,
    )
    base.update(over)
    return Namespace(**base)


def test_archive_enabled_from_yaml_survives_when_no_cli_flags(tmp_path):
    # Регрессия: раньше --zip (store_true, default False) всегда перезаписывал
    # archive.enabled, даже если флаг не передавался.
    config_file = tmp_path / "zip_project.yaml"
    config_file.write_text(
        "scan_dirs: ['.']\nsingle_files: []\narchive:\n  enabled: true\n",
        encoding="utf-8",
    )

    loader = ConfigLoader(cli_args=_cli())
    config = loader.load(str(config_file))

    assert config.archive.enabled is True


def test_dry_run_from_yaml_survives_when_no_cli_flag(tmp_path):
    config_file = tmp_path / "zip_project.yaml"
    config_file.write_text(
        "scan_dirs: ['.']\nsingle_files: []\ndry_run: true\n",
        encoding="utf-8",
    )

    loader = ConfigLoader(cli_args=_cli())
    config = loader.load(str(config_file))

    assert config.dry_run is True


def test_zip_cli_flag_overrides_yaml_when_explicitly_passed(tmp_path):
    config_file = tmp_path / "zip_project.yaml"
    config_file.write_text(
        "scan_dirs: ['.']\nsingle_files: []\narchive:\n  enabled: false\n",
        encoding="utf-8",
    )

    loader = ConfigLoader(cli_args=_cli(zip=True))
    config = loader.load(str(config_file))

    assert config.archive.enabled is True


def test_include_dir_cli_extends_scan_dirs(tmp_path):
    # Регрессия: loader раньше читал несуществующий cli.include_dirs
    # (вместо include_dir) и флаг --include-dir тихо игнорировался.
    config_file = tmp_path / "zip_project.yaml"
    config_file.write_text("scan_dirs: ['.']\nsingle_files: []\n", encoding="utf-8")

    loader = ConfigLoader(cli_args=_cli(include_dir=["extra"]))
    config = loader.load(str(config_file))

    assert "extra" in config.scan_dirs


def test_exclude_cli_extends_exclude_patterns(tmp_path):
    config_file = tmp_path / "zip_project.yaml"
    config_file.write_text("scan_dirs: ['.']\nsingle_files: []\n", encoding="utf-8")

    loader = ConfigLoader(cli_args=_cli(exclude=["**/extra_exclude"]))
    config = loader.load(str(config_file))

    assert "**/extra_exclude" in config.exclude_patterns


def test_output_cli_overrides_manifest_file(tmp_path):
    config_file = tmp_path / "zip_project.yaml"
    config_file.write_text("scan_dirs: ['.']\nsingle_files: []\n", encoding="utf-8")

    loader = ConfigLoader(cli_args=_cli(output="custom.txt"))
    config = loader.load(str(config_file))

    assert config.manifest.file == "custom.txt"


def test_base_dir_cli_overrides_base_working_dir(tmp_path):
    config_file = tmp_path / "zip_project.yaml"
    config_file.write_text("scan_dirs: ['.']\nsingle_files: []\n", encoding="utf-8")

    loader = ConfigLoader(cli_args=_cli(base_dir="somewhere"))
    config = loader.load(str(config_file))

    assert config.base_working_dir == "somewhere"
