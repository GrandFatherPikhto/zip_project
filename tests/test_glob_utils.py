from pathlib import Path

from zip_project.utils.glob_utils import matches_any, path_matches_pattern


def test_double_star_matches_dir_itself_anywhere():
    # Паттерн матчит именно узел "__pycache__" (используется сканером для
    # исключения самой директории через dirs.clear()), а не файлы внутри неё.
    assert path_matches_pattern(Path("__pycache__"), "**/__pycache__")
    assert path_matches_pattern(Path("src/pkg/__pycache__"), "**/__pycache__")
    assert not path_matches_pattern(Path("src/pkg"), "**/__pycache__")
    assert not path_matches_pattern(Path("__pycache__/cache.pyc"), "**/__pycache__")


def test_double_star_matches_zero_segments():
    # "**/old" должно матчить и "old" в корне, и "a/b/old"
    assert path_matches_pattern(Path("old"), "**/old")
    assert path_matches_pattern(Path("a/b/old"), "**/old")


def test_single_star_matches_one_segment():
    assert path_matches_pattern(Path("temp/file.tmp"), "temp/*")
    assert not path_matches_pattern(Path("temp/sub/file.tmp"), "temp/*")


def test_no_match_when_pattern_longer_than_path():
    assert not path_matches_pattern(Path("a"), "a/b")


def test_matches_any_true_if_any_pattern_matches():
    patterns = ["**/.git", "**/__pycache__", "**/old"]
    assert matches_any(Path("proj/old"), patterns)
    assert not matches_any(Path("proj/old/file.py"), patterns)  # матчится сам узел, не файлы внутри
    assert not matches_any(Path(".git/config"), patterns)
    assert not matches_any(Path("proj/src/file.py"), patterns)
