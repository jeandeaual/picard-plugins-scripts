from typing import Any, Dict
from uuid import uuid4

from picard.album import Album
from picard.metadata import Metadata
from pytest import fixture

from plugins.exclude_non_music_tracks.exclude_non_music_tracks import (
    ExcludeNonMusicTracks,
)


@fixture
def plugin() -> ExcludeNonMusicTracks:
    return ExcludeNonMusicTracks()


def test_exclude_non_music_tracks(
    plugin: ExcludeNonMusicTracks, album: Album
) -> None:
    album_id = str(uuid4())
    metadata = Metadata(
        {
            "musicbrainz_albumid": album_id,
            "label": "Test Label",
            "discnumber": 1,
            "totaldiscs": 2,
            "tracknumber": 1,
            "totaltracks": 2,
            "title": "Test Title",
            "album": "Test Album",
        }
    )
    track: Dict[str, Any] = {}
    release: Dict[str, Any] = {
        "media": [
            {
                "discs": [
                    {
                        "id": str(uuid4()),
                        "sectors": 73241,
                        "offsets": [150],
                        "offset-count": 1,
                    }
                ],
                "position": 1,
                "title": "Test CD 1",
                "format-id": "9712d52a-4509-3d4b-a1a2-67c88c643e31",
                "format": "CD",
                "track-count": 2,
                "track-offset": 0,
                "tracks": [
                    {
                        "id": str(uuid4()),
                        "title": "Test Track 1",
                        "length": 974546,
                        "number": "1",
                        "position": 1,
                        "artist-credit": [],
                        "recording": {
                            "id": str(uuid4()),
                            "title": "Test Recording 1",
                            "disambiguation": "",
                            "length": 974546,
                            "video": False,
                            "artist-credit": [],
                        },
                    },
                    {
                        "id": str(uuid4()),
                        "title": "Test Track 2",
                        "length": 974546,
                        "number": "2",
                        "position": 2,
                        "artist-credit": [],
                        "recording": {
                            "id": str(uuid4()),
                            "title": "Test Recording 2",
                            "disambiguation": "",
                            "length": 974546,
                            "video": True,
                            "artist-credit": [],
                        },
                    },
                ],
            },
            {
                "discs": [
                    {
                        "id": str(uuid4()),
                        "sectors": 73241,
                        "offsets": [150],
                        "offset-count": 1,
                    }
                ],
                "position": 2,
                "title": "Test DVD-Video 1",
                "format-id": "9712d52a-4509-3d4b-a1a2-67c88c643e31",
                "format": "DVD-Video",
                "track-count": 1,
                "track-offset": 0,
                "tracks": [
                    {
                        "id": str(uuid4()),
                        "title": "Test Track 3",
                        "length": 974546,
                        "number": "1",
                        "position": 1,
                        "artist-credit": [],
                        "recording": {
                            "id": str(uuid4()),
                            "title": "Test Recording 3",
                            "disambiguation": "",
                            "length": 974546,
                            "video": True,
                            "artist-credit": [],
                        },
                    },
                ],
            },
        ],
    }

    plugin.parse_release(album, metadata, release)
    plugin.set_track_count(album, metadata, track, release)

    assert len(metadata) == 8
    assert metadata["musicbrainz_albumid"] == album_id
    assert metadata["label"] == "Test Label"
    assert metadata["title"] == "Test Title"
    assert metadata["album"] == "Test Album"
    assert metadata["discnumber"] == "1"
    assert metadata["totaldiscs"] == "1"
    assert metadata["tracknumber"] == "1"
    assert metadata["totaltracks"] == "1"
