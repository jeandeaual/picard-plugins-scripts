"""Separate multiple catalog numbers per medium."""

from re import split as re_split
from typing import Any, Dict, List

from picard import log
from picard.album import Album
from picard.metadata import Metadata, register_track_metadata_processor


PLUGIN_NAME = "Separate multiple catalog numbers per medium"
PLUGIN_AUTHOR = "Alexis Jeandeau"
PLUGIN_DESCRIPTION = """
If a release has multiple catalog numbers, or a catalog number like
`ABCD 1000→1005` or `SQEX 10088~10094`, tag each disc with its own
catalog number.

This acts as a fix for
[this issue](https://musicbrainz.org/doc/Release/Catalog_Number):
> Some box sets will have a separate cat number for each disc, and then an
> overall number that appears on the outer packaging.
> It is currently not possible to enter them at the medium level, so they can
> either be added to the full release or listed in the annotation.
"""
PLUGIN_VERSION = "1.0"
PLUGIN_API_VERSIONS = [
    "2.7",
]
PLUGIN_LICENSE = "GPL-2.0-or-later"
PLUGIN_LICENSE_URL = "https://www.gnu.org/licenses/gpl-2.0.html"

_SPLIT_REGEX = r"→|~|～"
_SEPARATOR = "-"


def separate_catalog_numbers(
    _tagger: Album,
    metadata: Metadata,
    _track: Dict[str, Any],
    _release: Dict[str, Any],
) -> None:
    """Separate multiple catalog numbers per medium."""
    title: str = metadata["title"]

    if "label" not in metadata or "catalognumber" not in metadata:
        log.debug("No label or catalog number, skipping %s", title)
        return

    labels: List[str] = metadata.getraw("label")
    catalognumbers: List[str] = metadata.getraw("catalognumber")

    if len(labels) != 1:
        log.debug("Multiple or no labels, skipping %s", title)
        return

    if len(catalognumbers) == 1:
        catalognumber = catalognumbers[0]

        try:
            prefix, suffix = catalognumber.split(_SEPARATOR)
        except ValueError:
            log.warning("Invalid catalog number: %s", catalognumber)
            return

        try:
            low, high = re_split(_SPLIT_REGEX, suffix)
        except ValueError:
            log.debug("Single catalog number, skipping %s", title)
            return

        if len(low) != len(high):
            high = low[: len(low) - len(high)] + high

        try:
            catalognumbers = [
                f"{prefix}{_SEPARATOR}{number}"
                for number in range(int(low), int(high) + 1)
            ]
        except ValueError:
            log.warning("Invalid catalog number: %s", catalognumber)
            return

    discnumber = int(metadata["discnumber"])
    totaldiscs = int(metadata["totaldiscs"])

    if totaldiscs != len(catalognumbers):
        log.error(
            "The total disc count (%s) and "
            "the catalog number count (%d) do not match",
            totaldiscs,
            len(catalognumbers),
        )
        return

    catalognumber = catalognumbers[discnumber - 1]
    log.debug("Setting catalog number to %s for %s", catalognumber, title)
    metadata["catalognumber"] = [catalognumber]


register_track_metadata_processor(separate_catalog_numbers)
