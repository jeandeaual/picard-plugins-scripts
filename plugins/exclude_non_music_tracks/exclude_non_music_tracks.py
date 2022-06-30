"""Exclude non-music tracks from disc and track count."""

from collections import defaultdict
from typing import Any, DefaultDict, Dict, Set

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
    "2.8",
]
PLUGIN_LICENSE = "GPL-2.0-or-later"
PLUGIN_LICENSE_URL = "https://www.gnu.org/licenses/gpl-2.0.html"


class ExcludeNonMusicTracks:
    """MusicBrainz Picard plugin."""

    def __init__(self) -> None:
        self.media_to_skip: DefaultDict[str, Set[int]] = defaultdict(set)
        self.non_music_tracks: DefaultDict[
            str, DefaultDict[int, Set[int]]
        ] = defaultdict(lambda: defaultdict(set))

    def parse_release(
        self,
        _album: Album,
        metadata: Metadata,
        release: Dict[str, Any],
    ) -> None:
        """Album metadata processor."""
        media_count: int = 0

        try:
            album_id: str = metadata["musicbrainz_albumid"]
            media_to_skip = self.media_to_skip[album_id]
            non_music_tracks = self.non_music_tracks[album_id]

            for medium in release["media"]:
                medium_pos: int = medium["position"]

                if medium["format"] == "DVD-Video":
                    media_to_skip.add(medium_pos)
                    continue

                for track in medium["tracks"]:
                    if track["recording"]["video"]:
                        track_pos: int = track["position"]
                        non_music_tracks[medium_pos].add(track_pos)

                track_count: int = medium["track-count"]

                if (
                    medium_pos in non_music_tracks
                    and len(non_music_tracks[medium_pos]) == track_count
                ):
                    media_to_skip.add(medium_pos)
                    del non_music_tracks[medium_pos]
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
        try:
            album_id: str = metadata["musicbrainz_albumid"]

            if (
                album_id not in self.media_to_skip
                or album_id not in self.non_music_tracks
            ):
                return

            title: str = metadata["title"]
            discnumber = int(metadata["discnumber"])

            if discnumber in self.media_to_skip[album_id]:
                return

            disc_skip: int = 0
            for disc in range(1, discnumber + 1):
                if disc in self.media_to_skip[album_id]:
                    disc_skip += 1

            new_discnumber = discnumber - disc_skip

            log.debug(
                "Changing disc number from %d to %d for %s",
                discnumber,
                new_discnumber,
                title,
            )

            metadata["discnumber"] = new_discnumber

            if discnumber in self.non_music_tracks[album_id]:
                tracks_to_skip = self.non_music_tracks[album_id][discnumber]
                tracknumber = int(metadata["tracknumber"])
                totaltracks = int(metadata["totaltracks"])
                track_skip = 0

                for track in range(1, tracknumber + 1):
                    if track in tracks_to_skip:
                        track_skip += 1

                new_tracknumber = tracknumber - track_skip
                new_totaltracks = totaltracks - len(tracks_to_skip)

                log.debug(
                    "Changing track number from %d to %d "
                    "and total tracks from %d to %d for %s",
                    tracknumber,
                    new_tracknumber,
                    totaltracks,
                    new_totaltracks,
                    title,
                )

                metadata["tracknumber"] = new_tracknumber
                metadata["totaltracks"] = new_totaltracks
        except (KeyError, ValueError) as e:
            log.error("Error when setting the track count: %s", e)


plugin = ExcludeNonMusicTracks()

register_album_metadata_processor(plugin.parse_release)
register_track_metadata_processor(plugin.set_track_count)
