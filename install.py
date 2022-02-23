#!/usr/bin/env python3

"""Installs the plugins to the MusicBrainz Picard plugin folder.

Creates symlinks for single file plugins, creates and copies a ZIP file
for multi-files plugins.
"""

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from os import environ
from pathlib import Path
from platform import system
from sys import exit, stderr

from plugins import create_zip, get_plugin_dirs, rm_path


def path_from_env(variable: str, default: Path) -> Path:
    """Return a Path object from an environment variable."""
    value = environ.get(variable)
    if value:
        return Path(value)
    return default


def get_picard_user_plugin_dir() -> Path:
    """Return the MusicBrainz Picard plugin folder for the current user."""
    os_name = system()
    if os_name == "Windows":
        base_path = path_from_env(
            "LOCALAPPDATA",
            Path.home() / "AppData" / "Local",
        )
    elif os_name == "Darwin":
        base_path = Path.home() / "Library" / "Preferences"
    else:
        base_path = path_from_env("XDG_CONFIG_HOME", Path.home() / ".config")

    return base_path / "MusicBrainz" / "Picard" / "plugins"


def create_symlink(python_file: Path, plugin_dir: Path) -> None:
    """Create a symlink to a file in the MusicBrainz Picard plugin folder."""
    symlink = plugin_dir / python_file.name

    if symlink.is_symlink():
        print(f"Ignoring {symlink}...")
        return

    if symlink.exists():
        rm_path(symlink)

    symlink.symlink_to(python_file)

    print(f"Symlinked {symlink} to {symlink.resolve()}")


def main() -> None:
    """Program entrypoint."""
    parser = ArgumentParser(
        description=__doc__.strip(),
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        dest="dev",
        help="create symlinks for single-file plugins instead of archives",
    )
    args = parser.parse_args()

    user_plugin_dir = get_picard_user_plugin_dir()

    if not user_plugin_dir.is_dir():
        print(f"Plugin directory {user_plugin_dir} not found", file=stderr)
        exit(1)

    for plugin_dir in get_plugin_dirs():
        python_files = list(plugin_dir.glob("**/*.py"))
        if len(python_files) == 1:
            if args.dev:
                # Symlink the file
                create_symlink(python_files[0], user_plugin_dir)
            else:
                # Create a ZIP file and copy
                create_zip(plugin_dir, user_plugin_dir, single_file=True)
        elif len(python_files) > 1:
            if not any(
                str(python_file.relative_to(plugin_dir)) == "__init__.py"
                for python_file in python_files
            ):
                print(
                    f'No "__init__.py" file found in {plugin_dir}',
                    file=stderr,
                )
                exit(1)
            # Create a ZIP file and copy
            create_zip(plugin_dir, user_plugin_dir)


if __name__ == "__main__":
    main()
