from zip_project.cli import parse_args


def test_zip_flag_absent_is_none_not_false():
    # Регрессия: раньше --zip был action="store_true" без default=None,
    # из-за чего отсутствие флага (False) было неотличимо от "явно выключено"
    # и всегда затирало archive.enabled из YAML.
    args = parse_args([])
    assert args.zip is None
    assert args.dry_run is None


def test_zip_flag_present_is_true():
    args = parse_args(["--zip"])
    assert args.zip is True


def test_dry_run_flag_present_is_true():
    args = parse_args(["--dry-run"])
    assert args.dry_run is True


def test_include_dir_dest_matches_loader_expectation():
    # Регрессия: loader.py читает cli.include_dir (единственное число);
    # dest аргумента должен называться так же, а не include_dirs.
    args = parse_args(["--include-dir", "src", "--include-dir", "docs"])
    assert args.include_dir == ["src", "docs"]
    assert not hasattr(args, "include_dirs")
