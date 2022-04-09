from typing import Any, Dict

from picard.album import Album
from picard.metadata import Metadata

from plugins.separate_catalog_numbers.separate_catalog_numbers import (
    separate_catalog_numbers,
)


def test_separate_catalog_numbers_single(album: Album) -> None:
    metadata = Metadata(
        {
            "label": "Test Label",
            "catalognumber": "ABCD-0001",
            "discnumber": 2,
            "totaldiscs": 2,
            "title": "Test Title",
            "album": "Test Album",
        }
    )
    track: Dict[str, Any] = {}
    release: Dict[str, Any] = {}

    separate_catalog_numbers(album, metadata, track, release)

    assert len(metadata) == 6
    assert metadata["label"] == "Test Label"
    assert metadata["catalognumber"] == "ABCD-0001"
    assert metadata["discnumber"] == "2"
    assert metadata["totaldiscs"] == "2"
    assert metadata["title"] == "Test Title"
    assert metadata["album"] == "Test Album"


def test_separate_catalog_numbers_already_separated(album: Album) -> None:
    metadata = Metadata(
        {
            "label": ["Test Label", "Test Label"],
            "catalognumber": ["ABCD-0001", "ABCD-0002"],
            "discnumber": 2,
            "totaldiscs": 2,
            "title": "Test Title",
            "album": "Test Album",
        }
    )
    track: Dict[str, Any] = {}
    release: Dict[str, Any] = {}

    separate_catalog_numbers(album, metadata, track, release)

    assert len(metadata) == 6
    assert metadata.getraw("label") == ["Test Label", "Test Label"]
    assert metadata.getraw("catalognumber") == ["ABCD-0001", "ABCD-0002"]
    assert metadata["discnumber"] == "2"
    assert metadata["totaldiscs"] == "2"
    assert metadata["title"] == "Test Title"
    assert metadata["album"] == "Test Album"


def test_separate_catalog_numbers(album: Album) -> None:
    metadata = Metadata(
        {
            "label": "Test Label",
            "catalognumber": "ABCD-1001~1002",
            "discnumber": 2,
            "totaldiscs": 2,
            "title": "Test Title",
            "album": "Test Album",
        }
    )
    track: Dict[str, Any] = {}
    release: Dict[str, Any] = {}

    separate_catalog_numbers(album, metadata, track, release)

    assert len(metadata) == 6
    assert metadata["label"] == "Test Label"
    assert metadata["catalognumber"] == "ABCD-1002"
    assert metadata["discnumber"] == "2"
    assert metadata["totaldiscs"] == "2"
    assert metadata["title"] == "Test Title"
    assert metadata["album"] == "Test Album"
