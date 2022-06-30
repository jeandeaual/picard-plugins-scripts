from typing import List, Tuple

from pytest import mark

from plugins.korean_sort.korean_sort import HangulRomanizer


test_data: List[Tuple[str, str]] = [
    ("안녕하세요", "Annyeonghaseyo"),
    ("한글", "Hangeul"),
    ("제 이름은 테스트입니다.", "Je ireumeun teseuteuimnida."),
    ("식료품groceries", "Siglyopum groceries"),
    ("슈퍼마켓Yes! We’re Open", "Syupeomakes Yes! We’re Open"),
]


@mark.parametrize("string,expected", test_data)
def test_korean_sort(string: str, expected: str) -> None:
    assert HangulRomanizer().romanize(string) == expected
