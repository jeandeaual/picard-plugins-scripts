"""Album and track sorting using translations / transliterations."""

from functools import partial
from typing import Any, Dict

from PyQt5.QtNetwork import QNetworkReply

from picard import log
from picard.album import Album
from picard.metadata import (
    Metadata,
    register_album_metadata_processor,
    register_track_metadata_processor,
)
from picard.tagger import Tagger


PLUGIN_NAME = (
    "Set albumsort and titlesort using "
    "translation / transliteration relationships"
)
PLUGIN_AUTHOR = "Alexis Jeandeau"
PLUGIN_DESCRIPTION = """
Fetch latin script tracklists using translation / transliteration relationships
and use them to set the `albumsort` and `titlesort` tags.
"""
PLUGIN_VERSION = "1.0"
PLUGIN_API_VERSIONS = [
    "2.7",
]
PLUGIN_LICENSE = "GPL-2.0-or-later"
PLUGIN_LICENSE_URL = "https://www.gnu.org/licenses/gpl-2.0.html"


class TransliterationSort:
    """MusicBrainz Picard plugin."""

    SCRIPT = "Latn"

    def __init__(self):
        self.tracks: Dict[int, Dict[int, Dict[str, str]]] = {}

    def transliterated_release_dl_callback(
        self,
        album: Album,
        metadata: Metadata,
        document: Dict[str, Any],
        http: QNetworkReply,
        error: int,
    ) -> None:
        """MusicBrainz `get_release_by_id` callback."""
        self.tracks = {}

        try:
            if error:
                log.error(
                    "Error when querying the MusicBrainz API: %s",
                    http.errorString(),
                )
            else:
                if document["text-representation"]["script"] != self.SCRIPT:
                    return

                album_latin: str = document["title"]
                metadata["albumsort"] = album_latin

                medium: Dict[str, Any]
                for medium in document["media"]:
                    mediumpos: int = medium["position"]

                    self.tracks[mediumpos] = {}
                    for track in medium["tracks"]:
                        trackpos: int = track["position"]
                        title: str = track["title"]
                        recording_id: str = track["recording"]["id"]

                        self.tracks[mediumpos][trackpos] = {}

                        self.tracks[mediumpos][trackpos]["title"] = title
                        self.tracks[mediumpos][trackpos]["mbid"] = recording_id
        except KeyError as e:
            log.error("Error when parsing transliterated release: %s", e)
        finally:
            album._requests -= 1
            album._finalize_loading(None)

    def fetch_transliterations(
        self,
        album: Album,
        metadata: Metadata,
        release: Dict[str, Any],
    ) -> None:
        """Album metadata processor."""
        self.tracks = {}

        try:
            if (
                metadata["releasestatus"] != "pseudo-release"
                and metadata["script"] != self.SCRIPT
            ):
                relation: Dict[str, Any]
                for relation in release["relations"]:
                    if (
                        relation["target-type"] == "release"
                        and relation["type"] == "transl-tracklisting"
                        and relation["direction"] == "forward"
                    ):
                        release_id: str = relation["release"]["id"]
                        log.debug("Querying MB API for release %s", release_id)
                        album._requests += 1
                        tagger: Tagger = album.tagger
                        tagger.mb_api.get_release_by_id(
                            release_id,
                            partial(
                                self.transliterated_release_dl_callback,
                                album,
                                metadata,
                            ),
                            ["recordings"],
                        )
        except KeyError as e:
            log.error("Error when checking for transliterated releases: %s", e)

    def set_transliterations(
        self,
        _tagger: Album,
        metadata: Metadata,
        _track: Dict[str, Any],
        _release: Dict[str, Any],
    ) -> None:
        """Track metadata processor."""
        if not self.tracks:
            return

        try:
            discnumber = int(metadata["discnumber"])
            tracknumber = int(metadata["tracknumber"])
            track_info = self.tracks[discnumber][tracknumber]

            if track_info["mbid"] == metadata["musicbrainz_recordingid"]:
                log.debug(
                    "Setting titlesort for %s to %s",
                    metadata["title"],
                    track_info["title"],
                )
                metadata["titlesort"] = track_info["title"]
            else:
                log.error(
                    "MBID for %s (%s) does not match MBID for %s (%s).",
                    track_info["title"],
                    track_info["mbid"],
                    metadata["title"],
                    metadata["musicbrainz_trackid"],
                )
        except (KeyError, ValueError) as e:
            log.error("Error when setting track title transliterations: %s", e)


plugin = TransliterationSort()

register_album_metadata_processor(plugin.fetch_transliterations)
register_track_metadata_processor(plugin.set_transliterations)
