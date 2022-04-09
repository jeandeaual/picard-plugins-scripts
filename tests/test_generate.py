from json import load as json_load
from pathlib import Path

from pytest import fixture

from generate import build_json, zip_files
from lib import get_plugin_dirs


@fixture
def dest_dir(tmp_path: Path) -> Path:
    return tmp_path


@fixture
def json_file(dest_dir: Path) -> Path:
    return dest_dir / "plugins.json"


def test_get_plugin_dirs() -> None:
    assert len(get_plugin_dirs()) > 1


def test_build_json(dest_dir: Path, json_file: Path) -> None:
    build_json(dest_dir)

    with json_file.open("r", encoding="utf-8") as f:
        plugins_json = json_load(f)

    # All top level directories in the plugins directory
    plugin_dirs = get_plugin_dirs()

    assert "plugins" in plugins_json
    assert len(plugins_json["plugins"]) == len(plugin_dirs)

    for module_name, data in plugins_json["plugins"].items():
        assert type(module_name) is str
        assert type(data["name"]) is str
        assert type(data["api_versions"]) is list
        assert type(data["author"]) is str
        assert type(data["description"]) is str
        assert type(data["version"]) is str


def test_generate_zip(dest_dir: Path) -> None:
    zip_files(dest_dir)

    # All top level directories in the plugins directory
    plugin_dirs = get_plugin_dirs()

    # All zip files in plugin_dir
    plugin_zips = list(dest_dir.glob("*.zip"))

    # Number of folders should be equal to number of zips
    assert len(plugin_zips) == len(plugin_dirs)
