from typing import Any, Dict, List, Tuple

from picard.album import Album
from picard.metadata import Metadata
from picard.script import ScriptParser
from pytest import mark

from plugins.album_track_swap_sort.album_track_swap_sort import (
    delete_prefix,
    swap_sort_album,
    swap_sort_track,
)


test_data: List[Tuple[str, Tuple[str, str]]] = [
    ("The Album", ("Album", "The")),
    ("Un Album", ("Album", "Un")),
    ("L'album", ("Album", "L'")),
    ("L’album", ("Album", "L’")),
]


@mark.parametrize("string,expected", test_data)
def test_delete_prefix(string: str, expected: Tuple[str, str]) -> None:
    assert delete_prefix(None, string) == expected


@mark.parametrize("string,expected", test_data)
def test_swapprefixext_script_function(
    parser: ScriptParser, string: str, expected: Tuple[str, str]
) -> None:
    metadata = Metadata({"foo": string, "bar": "bar", "baz": "baz"})

    script = r"$set(bar,$swapprefixext(%foo%))"
    parser.eval(script, metadata)

    assert metadata["foo"] == string
    assert metadata["bar"] == ", ".join(expected)
    assert metadata["baz"] == "baz"
    assert len(metadata.keys()) == 3


@mark.parametrize("string,expected", test_data)
def test_swap_sort_album_track(
    album: Album, string: str, expected: Tuple[str, str]
) -> None:
    expected_string = ", ".join(expected)
    metadata = Metadata(
        {
            "album": string,
            "title": string,
            "dummy": "test",
        }
    )
    track: Dict[str, Any] = {}
    release: Dict[str, Any] = {}

    swap_sort_album(album, metadata, release)
    swap_sort_track(album, metadata, track, release)

    assert len(metadata) == 5
    assert metadata["album"] == string
    assert metadata["title"] == string
    assert metadata["albumsort"] == expected_string
    assert metadata["titlesort"] == expected_string
    assert metadata["dummy"] == "test"
