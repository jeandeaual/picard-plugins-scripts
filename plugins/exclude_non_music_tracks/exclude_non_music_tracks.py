"""Exclude non-music tracks from disc and track count."""

from collections import defaultdict
from typing import Any, Dict, Set

from picard import log
from picard.album import Album
from picard.metadata import (
    Metadata,
    register_album_metadata_processor,
    register_track_metadata_processor,
)


PLUGIN_NAME = "Exclude non-music tracks from disc and track count"
PLUGIN_AUTHOR = "Alexis Jeandeau"
PLUGIN_DESCRIPTION = """
Exclude non-music tracks from the disc and track count.
"""
PLUGIN_VERSION = "1.0"
PLUGIN_API_VERSIONS = [
    "2.0",
    "2.1",
    "2.2",
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "2.7",
]
PLUGIN_LICENSE = "GPL-2.0-or-later"
PLUGIN_LICENSE_URL = "https://www.gnu.org/licenses/gpl-2.0.html"


class ExcludeNonMusicTracks:
    """MusicBrainz Picard plugin."""

    def __init__(self):
        self.media_to_skip: Set[int] = set()
        self.non_music_tracks: defaultdict[int, Set[int]] = defaultdict(set)

    def parse_release(
        self,
        _album: Album,
        metadata: Metadata,
        release: Dict[str, Any],
    ) -> None:
        """Album metadata processor."""
        self.media_to_skip = set()
        self.non_music_tracks = defaultdict(set)

        media_count: int = 0

        try:
            for medium in release["media"]:
                medium_pos: int = medium["position"]

                if medium["format"] == "DVD-Video":
                    self.media_to_skip.add(medium_pos)
                    continue

                for track in medium["tracks"]:
                    if track["recording"]["video"]:
                        track_pos: int = track["position"]
                        self.non_music_tracks[medium_pos].add(track_pos)

                track_count: int = medium["track-count"]

                if (
                    medium_pos in self.non_music_tracks
                    and len(self.non_music_tracks[medium_pos]) == track_count
                ):
                    self.media_to_skip.add(medium_pos)
                    del self.non_music_tracks[medium_pos]
                    continue

                media_count += 1
        except KeyError as e:
            log.error("Error when parsing release: %s", e)

        if media_count != metadata["totaldiscs"]:
            metadata["totaldiscs"] = media_count

    def set_track_count(
        self,
        _tagger: Album,
        metadata: Metadata,
        _track: Dict[str, Any],
        _release: Dict[str, Any],
    ) -> None:
        """Track metadata processor."""
        if not self.media_to_skip and not self.non_music_tracks:
            return

        try:
            title: str = metadata["title"]
            discnumber = int(metadata["discnumber"])

            if discnumber in self.media_to_skip:
                return

            disc_skip: int = 0
            for disc in range(1, discnumber + 1):
                if disc in self.media_to_skip:
                    disc_skip += 1

            new_discnumber = discnumber - disc_skip

            log.debug(
                "Changing disc number from %d to %d for %s",
                discnumber,
                new_discnumber,
                title,
            )

            metadata["discnumber"] = new_discnumber

            tracknumber = int(metadata["tracknumber"])

            if discnumber in self.non_music_tracks:
                track_skip: int = 0
                for track in range(1, tracknumber + 1):
                    if track in self.non_music_tracks[discnumber]:
                        track_skip += 1

                new_tracknumber = tracknumber - track_skip

                log.debug(
                    "Changing track number from %d to %d for %s",
                    tracknumber,
                    new_tracknumber,
                    title,
                )

                metadata["tracknumber"] = new_tracknumber
        except (KeyError, ValueError) as e:
            log.error("Error when setting the track count: %s", e)


plugin = ExcludeNonMusicTracks()

register_album_metadata_processor(plugin.parse_release)
register_track_metadata_processor(plugin.set_track_count)
