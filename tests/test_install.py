from pathlib import Path

from pytest import MonkeyPatch, TempPathFactory

from install import create_symlink, get_picard_user_plugin_dir, path_from_env


def test_get_picard_user_plugin_dir() -> None:
    assert get_picard_user_plugin_dir() is not None


def test_path_from_env(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("TEST_PATH", False)

    default = Path("/tmp/default")  # noqa: S108

    path = path_from_env("TEST_PATH", default)
    assert str(path.as_posix()) == "/tmp/default"  # noqa: S108

    monkeypatch.setenv("TEST_PATH", "/tmp/test")  # noqa: S108

    path = path_from_env("TEST_PATH", default)
    assert str(path.as_posix()) == "/tmp/test"  # noqa: S108


def test_create_symlink(tmp_path_factory: TempPathFactory) -> None:
    source = tmp_path_factory.mktemp("source")
    target = tmp_path_factory.mktemp("target")

    file = source / "test.py"
    file.touch()

    create_symlink(file, target)

    symlink = target / "test.py"

    assert symlink.is_symlink()
    assert symlink.exists()
