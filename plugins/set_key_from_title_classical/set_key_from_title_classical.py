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
]
PLUGIN_LICENSE = "GPL-2.0-or-later"
PLUGIN_LICENSE_URL = "https://www.gnu.org/licenses/gpl-2.0.html"


_KEY_REGEX: Pattern[str] = re_compile(
    r"\sin\s"
    r"(?P<key>[A-G])(?:[-‐ ](?P<modifier>Flat|Sharp))?"
    r"(?:\s(?P<minor>minor))?",
    IGNORECASE,
)


def parse_key(
    _tagger: Album,
    metadata: Metadata,
    _track: Dict[str, Any],
    _release: Dict[str, Any],
) -> None:
    """Parse the key from the title and set the `key` tag."""
    if "Classical" not in metadata["genre"]:
        return

    match: Optional[Match[str]] = _KEY_REGEX.search(metadata["title"])

    if match:
        key: str = match.group("key").upper()
        modifier: Optional[str] = match.group("modifier")
        if modifier:
            if modifier.lower() == "sharp":
                key += "#"
            else:
                key += "b"
        if match.group("minor"):
            key += "m"

        log.debug("Setting the key of %s to %s", metadata["title"], key)

        metadata["key"] = key


register_track_metadata_processor(parse_key)
