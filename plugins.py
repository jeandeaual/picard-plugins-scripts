"""Picard plugin utilities."""

from pathlib import Path
from shutil import make_archive
from typing import List


# The directory which contains plugin files
PLUGIN_DIR = Path(__file__).parent / "plugins"


def get_plugin_dirs() -> List[Path]:
    """Get the list of plugin directories from this repository."""
    return [
        path
        for path in PLUGIN_DIR.iterdir()
        if path.is_dir() and path.name != ".git"
    ]


def rm_path(path: Path) -> None:
    """Delete a file or directory."""
    if path.exists():
        print(f"Deleting existing {path}...")
        if path.is_dir():
            path.rmdir()
        else:
            path.unlink()


def create_zip(
    script_dir: Path,
    dest_dir: Path,
    single_file: bool = False,
) -> None:
    """Create a ZIP archive in the destination folder."""
    archive = dest_dir / f"{script_dir.name}.zip"

    if archive.exists():
        rm_path(archive)

    make_archive(
        base_name=str(archive)[:-4],
        format="zip",
        root_dir=str(script_dir) if single_file else str(script_dir.parent),
        base_dir=None if single_file else script_dir.name,
    )

    print(f"Created {archive} from {script_dir}")
