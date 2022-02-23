"""Album / track / show swap sort."""

from re import match as re_match
from typing import Any, Dict, Tuple

from picard.album import Album
from picard.metadata import Metadata, register_track_metadata_processor
from picard.plugin import PluginPriority
from picard.script import ScriptParser, register_script_function


PLUGIN_NAME = "Album / track / show swap sort"
PLUGIN_AUTHOR = "Alexis Jeandeau"
PLUGIN_DESCRIPTION = """
Set `albumsort`, `titlesort` and `showsort` by swapping the prefix of the
corresponding tags (e.g. “A”, “The”, etc.).

Supports common prefixes for English, French, Spanish, Italian and German.
"""
PLUGIN_VERSION = "1.0"
PLUGIN_API_VERSIONS = [
    "2.6",
    "2.7",
]
PLUGIN_LICENSE = "GPL-2.0-or-later"
PLUGIN_LICENSE_URL = "https://www.gnu.org/licenses/gpl-2.0.html"

_SET_IF_SAME = False
_DEFAULT_PREFIXES = (
    # English
    "A ",
    "The ",
    # French
    "Un ",
    "Une ",
    "Des ",
    "Le ",
    "La ",
    "L'",
    "L’",
    # Spanish
    "Una ",
    "Unos ",
    "Unas",
    "El ",
    "Los ",
    "Las ",
    # Italian
    "Uno ",
    "Un'",
    "Un’",
    "Il ",
    "Lo ",
    "I ",
    "Gli ",
    # German
    "Der ",
    "Die ",
    "Das ",
    "Ein ",
    "Eine ",
)


def delete_prefix(
    _parser: ScriptParser,
    text: str,
    *prefixes: str,
) -> Tuple[str, str]:
    """Delete the specified prefixes from a string.

    Returns remaining string and deleted part separately.
    """
    if not prefixes:
        prefixes = _DEFAULT_PREFIXES
    text = text.strip()
    rx = (
        "("
        + ")|(".join(map(lambda prefix: prefix.replace(" ", r"\s+"), prefixes))
        + ")"
    )
    match = re_match(rx, text)
    if not match:
        return text, ""

    prefix = match.group()
    without_prefix = text[len(prefix) :]  # noqa: E203

    return f"{without_prefix[0].upper()}{without_prefix[1:]}", prefix.strip()


def swap_prefix(parser: ScriptParser, text: str, *prefixes: str) -> str:
    """Move the specified prefixes from the beginning to the end of `text`.

    Multiple prefixes can be specified as separate parameters.
    There are more default prefixes than the $swapprefix function of Picard.
    Also works with prefixes like L' (with no space after).
    """
    text, prefix = delete_prefix(parser, text, *prefixes)
    if prefix:
        return f"{text}, {prefix}"
    return text


def swap_sort_album_track(
    _tagger: Album,
    metadata: Metadata,
    _track: Dict[str, Any],
    _release: Dict[str, Any],
) -> None:
    """Set `titlesort`, `albumsort` and `showsort`.

    Swap the prefix of the `title`, `album` and `show` fields to set the
    corresponding sort fields.
    """
    for tag in ["title", "album", "show"]:
        if tag not in metadata:
            continue

        value: str = metadata[tag]
        swapped = swap_prefix(None, value)

        if swapped != value or _SET_IF_SAME:
            metadata[f"{tag}sort"] = swapped


register_script_function(
    swap_prefix,
    name="swapprefixext",
    check_argcount=False,
)
register_track_metadata_processor(swap_sort_album_track, PluginPriority.HIGH)
