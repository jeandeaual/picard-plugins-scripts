from typing import Any, Callable, Dict, Sequence
from uuid import uuid4

from PyQt5.QtNetwork import QNetworkReply
from iso639 import Lang
from picard.album import Album
from picard.metadata import Metadata
from pytest import fixture
from pytest_mock import MockerFixture

from plugins.transliteration_sort.transliteration_sort import (
    TransliterationSort,
)


@fixture
def plugin() -> TransliterationSort:
    return TransliterationSort()


def test_transliteration_sort_pseudorelease(
    plugin: TransliterationSort,
    album: Album,
    mocker: MockerFixture,
) -> None:
    get_release_by_id = mocker.patch.object(
        album.tagger.mb_api,
        "get_release_by_id",
        autospec=True,
    )

    album_id = str(uuid4())
    metadata = Metadata(
        {
            "musicbrainz_albumid": album_id,
            "releasestatus": "pseudo-release",
            "script": "Latn",
            "discnumber": 1,
            "totaldiscs": 1,
            "tracknumber": 1,
            "totaltracks": 1,
        }
    )
    track: Dict[str, Any] = {}
    release: Dict[str, Any] = {
        "relations": [
            {
                "target-type": "release",
                "type": "transl-tracklisting",
                "direction": "forward",
                "release": {
                    "id": str(uuid4()),
                },
            },
        ],
    }

    plugin.fetch_transliterations(album, metadata, release)
    plugin.set_transliterations(album, metadata, track, release)

    get_release_by_id.assert_not_called()

    assert len(metadata) == 7
    assert metadata["musicbrainz_albumid"] == album_id
    assert metadata["releasestatus"] == "pseudo-release"
    assert metadata["script"] == "Latn"
    assert metadata["discnumber"] == "1"
    assert metadata["totaldiscs"] == "1"
    assert metadata["tracknumber"] == "1"
    assert metadata["totaltracks"] == "1"


def test_transliteration_sort(
    plugin: TransliterationSort,
    album: Album,
    mocker: MockerFixture,
) -> None:
    transliterated_release_id = str(uuid4())
    album_id = str(uuid4())
    recording_id = str(uuid4())

    def callback(
        releaseid: str,
        _handler: Callable[[Dict[str, Any], QNetworkReply, int], None],
        _inc: Sequence[str] = None,
        _priority: bool = False,
        _important: bool = False,
        _mblogin: bool = False,
        _refresh: bool = False,
    ) -> None:
        assert releaseid == transliterated_release_id

        document: Dict[str, Any] = {
            "text-representation": {"script": "Latn"},
            "title": "Transliterated Test Album",
            "media": [
                {
                    "position": 1,
                    "tracks": [
                        {
                            "position": 1,
                            "title": "Transliterated Test Title",
                            "recording": {
                                "id": recording_id,
                            },
                        },
                    ],
                },
            ],
        }

        plugin.transliterated_release_dl_callback(
            album,
            metadata,
            document,
            mocker.MagicMock(auto_spec=QNetworkReply),
            0,
        )

    get_release_by_id = mocker.patch.object(
        album.tagger.mb_api,
        "get_release_by_id",
        autospec=True,
        side_effect=callback,
    )

    metadata = Metadata(
        {
            "musicbrainz_albumid": album_id,
            "musicbrainz_recordingid": recording_id,
            "releasestatus": "official",
            "script": "Japanese",
            "discnumber": 1,
            "totaldiscs": 1,
            "tracknumber": 1,
            "totaltracks": 1,
            "title": "Test Title",
            "album": "Test Album",
        }
    )
    track: Dict[str, Any] = {}
    release: Dict[str, Any] = {
        "relations": [
            {
                "target-type": "release",
                "type": "transl-tracklisting",
                "direction": "forward",
                "release": {
                    "id": transliterated_release_id,
                    "disambiguation": "",
                    "text-representation": {
                        "language": Lang("English").pt3,
                    },
                },
            },
        ],
    }

    plugin.fetch_transliterations(album, metadata, release)
    plugin.set_transliterations(album, metadata, track, release)

    get_release_by_id.assert_called_once()

    assert len(metadata) == 12
    assert metadata["musicbrainz_albumid"] == album_id
    assert metadata["musicbrainz_recordingid"] == recording_id
    assert metadata["releasestatus"] == "official"
    assert metadata["script"] == "Japanese"
    assert metadata["discnumber"] == "1"
    assert metadata["totaldiscs"] == "1"
    assert metadata["tracknumber"] == "1"
    assert metadata["totaltracks"] == "1"
    assert metadata["title"] == "Test Title"
    assert metadata["album"] == "Test Album"
    assert metadata["albumsort"] == "Transliterated Test Album"
    assert metadata["titlesort"] == "Transliterated Test Title"
