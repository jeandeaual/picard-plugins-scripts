from gettext import gettext
from typing import Any, Callable, Sequence

from PyQt5.QtCore import QObject, pyqtSignal
from picard import album as album_package, config, log
from picard.album import Album
from picard.script import ScriptParser
from picard.webservice import WebService
from picard.webservice.api_helpers import MBAPIHelper
from pytest import fixture
from pytest_mock import MockerFixture


# Inject missing import in album
album_package._ = gettext


class FakeTagger(QObject):
    tagger_stats_changed = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        QObject.config = config  # type: ignore
        QObject.log = log  # type: ignore
        self.tagger_stats_changed.connect(self.emit)
        self.exit_cleanup = []  # type: ignore
        self.files = {}  # type: ignore
        self.stopping = False

    def register_cleanup(self, func: Callable[..., None]) -> None:
        self.exit_cleanup.append(func)

    def run_cleanup(self) -> None:
        for f in self.exit_cleanup:
            f()

    def emit(self, *args: Sequence[Any]) -> None:
        pass


@fixture
def parser() -> ScriptParser:
    return ScriptParser()


@fixture
def album(mocker: MockerFixture) -> Album:
    album = mocker.MagicMock(auto_spec=Album)
    album.tagger = FakeTagger()
    album.tagger.mb_api = MBAPIHelper(  # type: ignore
        mocker.MagicMock(auto_spec=WebService),
    )
    return album
