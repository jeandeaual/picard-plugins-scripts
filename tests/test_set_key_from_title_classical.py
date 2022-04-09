from typing import Any, Dict

from iso639 import Lang
from picard.album import Album
from picard.metadata import Metadata

from plugins.set_key_from_title_classical.set_key_from_title_classical import (
    parse_key,
)


def test_set_key_from_title_classical_default_english(album: Album) -> None:
    metadata = Metadata(
        {
            "genre": "Classical",
            "script": "Latn",
            "title": "Test in F-sharp major",
        }
    )
    track: Dict[str, Any] = {}
    release: Dict[str, Any] = {}

    parse_key(album, metadata, track, release)

    assert len(metadata) == 4
    assert metadata["genre"] == "Classical"
    assert metadata["script"] == "Latn"
    assert metadata["title"] == "Test in F-sharp major"
    assert metadata["key"] == "F#"

    metadata = Metadata(
        {
            "genre": "Classical",
            "script": "Latn",
            "title": "Test in C-flat minor",
        }
    )

    parse_key(album, metadata, track, release)

    assert len(metadata) == 4
    assert metadata["genre"] == "Classical"
    assert metadata["script"] == "Latn"
    assert metadata["title"] == "Test in C-flat minor"
    assert metadata["key"] == "Cbm"

    metadata = Metadata(
        {
            "genre": "Classical",
            "script": "Latn",
            "title": "Test in H-Moll",
        }
    )

    parse_key(album, metadata, track, release)

    assert len(metadata) == 3
    assert metadata["genre"] == "Classical"
    assert metadata["script"] == "Latn"
    assert metadata["title"] == "Test in H-Moll"


def test_set_key_from_title_classical_german(album: Album) -> None:
    language_code = Lang("German").pt3
    metadata = Metadata(
        {
            "~releaselanguage": language_code,
            "genre": "Classical",
            "script": "Latn",
            "title": "Test in Fis-Dur",
        }
    )
    track: Dict[str, Any] = {}
    release: Dict[str, Any] = {}

    parse_key(album, metadata, track, release)

    assert len(metadata) == 5
    assert metadata["~releaselanguage"] == language_code
    assert metadata["genre"] == "Classical"
    assert metadata["script"] == "Latn"
    assert metadata["title"] == "Test in Fis-Dur"
    assert metadata["key"] == "F#"

    metadata = Metadata(
        {
            "~releaselanguage": language_code,
            "genre": "Classical",
            "script": "Latn",
            "title": "Test in H-Moll",
        }
    )

    parse_key(album, metadata, track, release)

    assert len(metadata) == 5
    assert metadata["~releaselanguage"] == language_code
    assert metadata["genre"] == "Classical"
    assert metadata["script"] == "Latn"
    assert metadata["title"] == "Test in H-Moll"
    assert metadata["key"] == "Bm"


def test_set_key_from_title_classical_french(album: Album) -> None:
    language_code = Lang("French").pt3
    metadata = Metadata(
        {
            "~releaselanguage": language_code,
            "genre": "Classical",
            "script": "Latn",
            "title": "Test en ré bémol majeur",
        }
    )
    track: Dict[str, Any] = {}
    release: Dict[str, Any] = {}

    parse_key(album, metadata, track, release)

    assert len(metadata) == 5
    assert metadata["~releaselanguage"] == language_code
    assert metadata["genre"] == "Classical"
    assert metadata["script"] == "Latn"
    assert metadata["title"] == "Test en ré bémol majeur"
    assert metadata["key"] == "Db"

    metadata = Metadata(
        {
            "~releaselanguage": language_code,
            "genre": "Classical",
            "script": "Latn",
            "title": "Test en do mineur",
        }
    )

    parse_key(album, metadata, track, release)

    assert len(metadata) == 5
    assert metadata["~releaselanguage"] == language_code
    assert metadata["genre"] == "Classical"
    assert metadata["script"] == "Latn"
    assert metadata["title"] == "Test en do mineur"
    assert metadata["key"] == "Cm"


def test_set_key_from_title_classical_italian(album: Album) -> None:
    language_code = Lang("Italian").pt3
    metadata = Metadata(
        {
            "~releaselanguage": language_code,
            "genre": "Classical",
            "script": "Latn",
            "title": "Test in fa diesis minore",
        }
    )
    track: Dict[str, Any] = {}
    release: Dict[str, Any] = {}

    parse_key(album, metadata, track, release)

    assert len(metadata) == 5
    assert metadata["~releaselanguage"] == language_code
    assert metadata["genre"] == "Classical"
    assert metadata["script"] == "Latn"
    assert metadata["title"] == "Test in fa diesis minore"
    assert metadata["key"] == "F#m"

    metadata = Metadata(
        {
            "~releaselanguage": language_code,
            "genre": "Classical",
            "script": "Latn",
            "title": "Test in sol majore",
        }
    )

    parse_key(album, metadata, track, release)

    assert len(metadata) == 5
    assert metadata["~releaselanguage"] == language_code
    assert metadata["genre"] == "Classical"
    assert metadata["script"] == "Latn"
    assert metadata["title"] == "Test in sol majore"
    assert metadata["key"] == "G"
