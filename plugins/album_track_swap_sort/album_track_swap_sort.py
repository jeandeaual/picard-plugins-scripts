"""Album / track / show swap sort."""

from re import match as re_match
from typing import Any, Dict, Iterable, Tuple

from picard import log
from picard.album import Album
from picard.metadata import (
    Metadata,
    register_album_metadata_processor,
    register_track_metadata_processor,
)
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
    "2.8",
]
PLUGIN_LICENSE = "GPL-2.0-or-later"
PLUGIN_LICENSE_URL = "https://www.gnu.org/licenses/gpl-2.0.html"

_SET_IF_SAME = False
_DEFAULT_PREFIXES: Dict[str, Tuple[str, ...]] = {
    # English
    "eng": (
        "A ",
        "The ",
    ),
    # French
    "fra": (
        "Un ",
        "Une ",
        "Des ",
        "Le ",
        "La ",
        "L'",
        "L’",
    ),
    # Spanish
    "spa": (
        "Una ",
        "Unos ",
        "Unas",
        "El ",
        "Los ",
        "Las ",
    ),
    # Italian
    "ita": (
        "Uno ",
        "Un'",
        "Un’",
        "Il ",
        "Lo ",
        "I ",
        "Gli ",
    ),
    # German
    "ger": (
        "Der ",
        "Die ",
        "Das ",
        "Ein ",
        "Eine ",
    ),
}


def delete_prefix(
    _parser: ScriptParser,
    text: str,
    *prefixes: str,
) -> Tuple[str, str]:
    """Delete the specified prefixes from a string.

    Returns remaining string and deleted part separately.
    """
    if not prefixes:
        prefixes = (
            _DEFAULT_PREFIXES["eng"]
            + _DEFAULT_PREFIXES["fra"]
            + _DEFAULT_PREFIXES["spa"]
        )
    text = text.strip()
    regex = (
        "("
        + ")|(".join(map(lambda prefix: prefix.replace(" ", r"\s+"), prefixes))
        + ")"
    )
    match = re_match(regex, text)
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


def swap_sort_tags(metadata: Metadata, tags: Iterable[str]) -> None:
    """Swap the prefix of `tags` to set the corresponding sort fields."""
    language = metadata["~releaselanguage"]

    if language != "eng" and language in _DEFAULT_PREFIXES:
        prefixes = _DEFAULT_PREFIXES[language] + _DEFAULT_PREFIXES["eng"]
    else:
        # Use the defaults
        prefixes = ()

    for tag in tags:
        if tag not in metadata:
            continue

        value: str = metadata[tag]
        swapped = swap_prefix(None, value, *prefixes)

        if swapped != value or _SET_IF_SAME:
            sort_tag = f"{tag}sort"
            log.debug("Setting %s to %s", sort_tag, swapped)
            metadata[sort_tag] = swapped


def swap_sort_album(
    _tagger: Album,
    metadata: Metadata,
    _release: Dict[str, Any],
) -> None:
    """Swap the prefix of the `album` fields to set the `albumsort` field."""
    swap_sort_tags(metadata, ["album"])


def swap_sort_track(
    _tagger: Album,
    metadata: Metadata,
    _track: Dict[str, Any],
    _release: Dict[str, Any],
) -> None:
    """Set `titlesort` and `showsort`.

    Swap the prefix of the `title` and `show` fields to set the corresponding
    sort fields.
    """
    swap_sort_tags(metadata, ["title", "show"])


register_script_function(
    swap_prefix,
    name="swapprefixext",
    check_argcount=False,
)
register_album_metadata_processor(swap_sort_album, PluginPriority.HIGH)
register_track_metadata_processor(swap_sort_track, PluginPriority.HIGH)
