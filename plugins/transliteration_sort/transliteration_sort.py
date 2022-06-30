"""Album and track sorting using translations / transliterations."""

from collections import defaultdict
from functools import partial
from typing import Any, DefaultDict, Dict, List

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
    "2.8",
]
PLUGIN_LICENSE = "GPL-2.0-or-later"
PLUGIN_LICENSE_URL = "https://www.gnu.org/licenses/gpl-2.0.html"


class TransliterationSort:
    """MusicBrainz Picard plugin."""

    SCRIPT = "Latn"

    def __init__(self) -> None:
        self.tracks: DefaultDict[
            str, DefaultDict[int, DefaultDict[int, Dict[str, str]]]
        ] = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    def transliterated_release_dl_callback(
        self,
        album: Album,
        metadata: Metadata,
        document: Dict[str, Any],
        http: QNetworkReply,
        error: int,
    ) -> None:
        """MusicBrainz `get_release_by_id` callback."""
        try:
            if error:
                log.error(
                    "Error when querying the MusicBrainz API: %s",
                    http.errorString(),
                )
                return

            if document["text-representation"]["script"] != self.SCRIPT:
                return

            album_latin: str = document["title"]
            metadata["albumsort"] = album_latin

            original_album_id: str = metadata["musicbrainz_albumid"]

            medium: Dict[str, Any]
            for medium in document["media"]:
                mediumpos: int = medium["position"]

                track: Dict[str, Any]
                for track in medium["tracks"]:
                    trackpos: int = track["position"]
                    title: str = track["title"]
                    recording_id: str = track["recording"]["id"]

                    log.debug(
                        "Found transliterated title for %s %d-%d: %s",
                        metadata["album"],
                        mediumpos,
                        trackpos,
                        title,
                    )

                    self.tracks[original_album_id][mediumpos][trackpos] = {
                        "title": title,
                        "mbid": recording_id,
                    }
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
        try:
            if (
                metadata["releasestatus"] == "pseudo-release"
                or metadata["script"] == self.SCRIPT
            ):
                return

            transl_release_ids: List[str] = []

            relation: Dict[str, Any]
            for relation in release["relations"]:
                if (
                    relation["target-type"] == "release"
                    and relation["type"] == "transl-tracklisting"
                    and relation["direction"] == "forward"
                ):
                    transl_release: Dict[str, Any] = relation["release"]
                    log.debug(
                        "Found transliterated / translated release %s",
                        transl_release,
                    )

                    disambiguation: str = transl_release[
                        "disambiguation"
                    ].lower()
                    language: str = transl_release["text-representation"][
                        "language"
                    ]

                    release_id: str = transl_release["id"]
                    if "transliterated" in disambiguation or (
                        language and language != "eng"
                    ):
                        # Prioritize transliterations over translations
                        # This is sometimes specified in the disambiguation
                        transl_release_ids.insert(0, release_id)
                    else:
                        transl_release_ids.append(release_id)

            if not transl_release_ids:
                return

            release_id = transl_release_ids[0]
            log.info(
                "Querying MB API for release %s (transliteration of %s)",
                release_id,
                metadata["album"],
            )
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
        try:
            album_id = metadata["musicbrainz_albumid"]
            discnumber = int(metadata["discnumber"])
            tracknumber = int(metadata["tracknumber"])

            if (
                not self.tracks
                or album_id not in self.tracks
                or discnumber not in self.tracks[album_id]
                or tracknumber not in self.tracks[album_id][discnumber]
            ):
                return

            track_info = self.tracks[album_id][discnumber][tracknumber]

            if track_info["mbid"] == metadata["musicbrainz_recordingid"]:
                if track_info["title"] != metadata["title"]:
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
                    metadata["musicbrainz_recordingid"],
                )

            # Cleanup fetched data
            del self.tracks[album_id][discnumber][tracknumber]
            if not self.tracks[album_id][discnumber]:
                del self.tracks[album_id][discnumber]
            if not self.tracks[album_id]:
                del self.tracks[album_id]
        except (KeyError, ValueError) as e:
            log.error("Error when setting track title transliterations: %s", e)


plugin = TransliterationSort()

register_album_metadata_processor(plugin.fetch_transliterations)
register_track_metadata_processor(plugin.set_transliterations)
