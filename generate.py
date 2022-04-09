#!/usr/bin/env python3

"""Generate the plugins' JSON data and/or ZIP files."""

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from ast import (
    Assign,
    Name,
    Store,
    dump as ast_dump,
    iter_child_nodes,
    literal_eval,
    parse as ast_parse,
)
from hashlib import md5
from json import dump as json_dump
from pathlib import Path, PurePosixPath
from sys import stderr
from typing import Dict, Union

from lib import create_zip, get_plugin_dirs


# The file that contains json data
PLUGIN_FILE = "plugins.json"

# Known metadata for Picard plugins
KNOWN_DATA = [
    "PLUGIN_NAME",
    "PLUGIN_AUTHOR",
    "PLUGIN_VERSION",
    "PLUGIN_API_VERSIONS",
    "PLUGIN_LICENSE",
    "PLUGIN_LICENSE_URL",
    "PLUGIN_DESCRIPTION",
]

PluginMetadata = Dict[str, Union[str, Dict[str, str]]]


def get_plugin_data(filepath: str) -> PluginMetadata:
    """Parse a Python file and return a dict with plugin metadata."""
    data: PluginMetadata = {}

    with open(filepath, "r", encoding="utf-8") as plugin_file:
        source = plugin_file.read()

    root = ast_parse(source, filepath)

    for node in iter_child_nodes(root):
        if not isinstance(node, Assign) or len(node.targets) != 1:
            continue

        target = node.targets[0]

        if (
            not isinstance(target, Name)
            or not isinstance(target.ctx, Store)
            or target.id not in KNOWN_DATA
        ):
            continue

        name = target.id.replace("PLUGIN_", "", 1).lower()
        if name not in data:
            try:
                value = literal_eval(node.value)
                if isinstance(value, str):
                    data[name] = value.strip()
                else:
                    data[name] = value
            except ValueError:
                print(
                    f"Cannot evaluate value in {filepath}: "
                    f"{ast_dump(node)}"
                )

    return data


def build_json(dest_dir: Path) -> None:
    """Traverse the plugins directory to generate JSON data."""
    plugins: Dict[str, PluginMetadata] = {}

    for plugin_dir in get_plugin_dirs():
        files: Dict[str, str] = {}
        data: PluginMetadata = {}

        script_files = [f for f in plugin_dir.glob("**/*") if f.is_file()]

        for script_file in script_files:
            ext = script_file.suffix

            if ext != ".pyc":
                with open(script_file, "rb") as md5file:
                    md5_hash = md5(md5file.read()).hexdigest()  # noqa: S303
                files[
                    str(PurePosixPath(script_file.relative_to(plugin_dir)))
                ] = md5_hash

                if ext == ".py" and not data:
                    try:
                        data = get_plugin_data(str(script_file))
                    except ValueError:
                        print(f"Cannot parse {script_file}")
                        raise

        if files and data:
            print(f"Added {plugin_dir.name}")
            data["files"] = files
            plugins[plugin_dir.name] = data

    out_path = dest_dir / PLUGIN_FILE

    with open(out_path, "w") as out_file:
        json_dump({"plugins": plugins}, out_file, sort_keys=True, indent=2)


def zip_files(dest_dir: Path) -> None:
    """Zip up the plugin folders."""
    for plugin_dir in get_plugin_dirs():
        python_files = list(plugin_dir.glob("**/*.py"))
        if len(python_files) == 1:
            create_zip(plugin_dir, dest_dir, single_file=True)
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
            create_zip(plugin_dir, dest_dir)


if __name__ == "__main__":
    parser = ArgumentParser(
        description=__doc__.strip(),
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--build-dir",
        default="build",
        type=Path,
        help="path for the build output",
    )
    parser.add_argument(
        "--no-zip",
        action="store_false",
        dest="zip",
        help="Do not generate the zip files in the build output",
    )
    parser.add_argument(
        "--no-json",
        action="store_false",
        dest="json",
        help="Do not generate the json file in the build output",
    )
    args = parser.parse_args()

    dest_dir: Path = args.build_dir
    dest_dir.mkdir(parents=True, exist_ok=True)

    if args.json:
        build_json(dest_dir)
    if args.zip:
        zip_files(dest_dir)
