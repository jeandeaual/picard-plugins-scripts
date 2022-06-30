"""Set the initial key from the track title for classical releases."""

from re import IGNORECASE, compile as re_compile
from typing import Any, Dict, Match, Optional, Pattern

from picard import log
from picard.album import Album
from picard.metadata import Metadata, register_track_metadata_processor


PLUGIN_NAME = "Set the initial key from the track title for classical releases"
PLUGIN_AUTHOR = "Alexis Jeandeau"
PLUGIN_DESCRIPTION = """
Set the initial key from the track title for classical releases.

For example, set the key tag to `C#m` for a track called
`Symphony No. 5 In C-Sharp Minor`.
"""
PLUGIN_VERSION = "1.0"
PLUGIN_API_VERSIONS = [
    "2.7",
    "2.8",
]
PLUGIN_LICENSE = "GPL-2.0-or-later"
PLUGIN_LICENSE_URL = "https://www.gnu.org/licenses/gpl-2.0.html"


_KEY_REGEXES: Dict[str, Pattern[str]] = {
    # English
    "eng": re_compile(
        r"\sin\s"
        r"(?P<key>[A-G])(?:[-‐\s](?P<modifier>Flat|Sharp))?"
        r"(?:\s(?P<minor>minor))?",
        IGNORECASE,
    ),
    # German
    "deu": re_compile(
        r"\sin\s"
        r"(?P<key>[A-H])(?P<modifier>es|is)?"
        r"(?:[\s\-‐](?P<minor>Moll))?",
        IGNORECASE,
    ),
    # French
    "fra": re_compile(
        r"\sen\s"
        r"(?P<key>do|ré|mi|fa|sol|la|si)(?:\s(?P<modifier>bémol|dièse))?"
        r"(?:\s(?P<minor>mineur))?",
        IGNORECASE,
    ),
    # Italian
    "ita": re_compile(
        r"\sin\s"
        r"(?P<key>do|re|mi|fa|sol|la|si)(?:\s(?P<modifier>bemolle|diesis))?"
        r"(?:\s(?P<minor>minore))?",
        IGNORECASE,
    ),
}


def parse_key(
    _tagger: Album,
    metadata: Metadata,
    _track: Dict[str, Any],
    _release: Dict[str, Any],
) -> None:
    """Parse the key from the title and set the `key` tag."""
    language = metadata["~releaselanguage"]
    regex = (
        _KEY_REGEXES[language]
        if language in _KEY_REGEXES
        else _KEY_REGEXES["eng"]
    )

    match: Optional[Match[str]] = regex.search(metadata["title"])

    if not match:
        return

    # See TKEY in https://id3.org/id3v2.3.0
    key: str = match.group("key").upper()
    if language == "deu":
        if key == "H":
            key = "B"
        elif key == "B":
            key = "Bb"
    elif language == "fra" or language == "ita":
        if key == "DO":
            key = "C"
        elif key == "RE" or key == "RÉ":
            key = "D"
        elif key == "MI":
            key = "E"
        elif key == "FA":
            key = "F"
        elif key == "SOL":
            key = "G"
        elif key == "LA":
            key = "A"
        elif key == "SI":
            key = "B"
    modifier: Optional[str] = match.group("modifier")
    if modifier:
        if modifier.lower() in ["sharp", "is", "dièse", "diesis"]:
            key += "#"
        else:
            key += "b"
    if match.group("minor"):
        key += "m"

    log.debug("Setting the key of %s to %s", metadata["title"], key)

    metadata["key"] = key


register_track_metadata_processor(parse_key)
