"""Korean sort plugin."""

PLUGIN_NAME = "Korean sort"
PLUGIN_AUTHOR = "Alexis Jeandeau"
PLUGIN_DESCRIPTION = """
Set albumsort and titlesort based on the transliteration of hangeul.
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

VOWELS = (
    "ㅏ",
    "ㅐ",
    "ㅑ",
    "ㅒ",
    "ㅓ",
    "ㅔ",
    "ㅕ",
    "ㅖ",
    "ㅗ",
    "ㅘ",
    "ㅙ",
    "ㅚ",
    "ㅛ",
    "ㅜ",
    "ㅝ",
    "ㅞ",
    "ㅟ",
    "ㅠ",
    "ㅡ",
    "ㅢ",
    "ㅣ",
)
CONSONANTS = (
    "ㄱ",
    "ㄲ",
    "ㄳ",
    "ㄴ",
    "ㄵ",
    "ㄶ",
    "ㄷ",
    "ㄸ",
    "ㄹ",
    "ㄺ",
    "ㄻ",
    "ㄼ",
    "ㄽ",
    "ㄾ",
    "ㄿ",
    "ㅀ",
    "ㅁ",
    "ㅂ",
    "ㅃ",
    "ㅄ",
    "ㅅ",
    "ㅆ",
    "ㅇ",
    "ㅈ",
    "ㅉ",
    "ㅊ",
    "ㅋ",
    "ㅌ",
    "ㅍ",
    "ㅎ",
)
INITIALS = (
    "ㄱ",
    "ㄲ",
    "ㄴ",
    "ㄷ",
    "ㄸ",
    "ㄹ",
    "ㅁ",
    "ㅂ",
    "ㅃ",
    "ㅅ",
    "ㅆ",
    "ㅇ",
    "ㅈ",
    "ㅉ",
    "ㅊ",
    "ㅋ",
    "ㅌ",
    "ㅍ",
    "ㅎ",
)
FINALS = (
    "",
    "ㄱ",
    "ㄲ",
    "ㄳ",
    "ㄴ",
    "ㄵ",
    "ㄶ",
    "ㄷ",
    "ㄹ",
    "ㄺ",
    "ㄻ",
    "ㄼ",
    "ㄽ",
    "ㄾ",
    "ㄿ",
    "ㅀ",
    "ㅁ",
    "ㅂ",
    "ㅄ",
    "ㅅ",
    "ㅆ",
    "ㅇ",
    "ㅈ",
    "ㅊ",
    "ㅋ",
    "ㅌ",
    "ㅍ",
    "ㅎ",
)
HANGUL_RANGE = range(ord("가"), ord("힣") + 1)
FIRST_HANGUL = HANGUL_RANGE[0]


def char_offset(char) -> int:
    """Returns Hangul character offset from "가"."""
    if isinstance(char, int):
        offset = char
    else:
        assert len(char) == 1
        assert is_hangul(char)
        offset = ord(char) - FIRST_HANGUL
    assert offset < len(HANGUL_RANGE)
    return offset


def is_hangul(char):
    """Checks if the given character is written in Hangul."""
    return ord(char) in HANGUL_RANGE


def is_vowel(char):
    """Checks if the given character is a vowel of Hangul."""
    return char in VOWELS


def is_consonant(char):
    """Checks if the given character is a consonant of Hangul."""
    return char in CONSONANTS


def is_initial(char):
    """Checks if the given character is an initial consonant of Hangul."""
    return char in INITIALS


def is_final(char):
    """Checks if the given character is a final consonant of Hangul. The final
    consonants contain what a joined multiple consonant and empty character.
    """
    return char in FINALS


def get_initial(char):
    """Returns an initial consonant from the given character."""
    if is_initial(char):
        return char
    return INITIALS[char_offset(char) // (len(VOWELS) * len(FINALS))]


def get_vowel(char):
    """Returns a vowel from the given character."""
    if is_vowel(char):
        return char
    return VOWELS[(char_offset(char) // len(FINALS)) % len(VOWELS)]


def get_final(char):
    """Returns a final consonant from the given character."""
    if is_final(char):
        return char
    return FINALS[char_offset(char) % len(FINALS)]


# -*- coding: utf-8 -*-

# Terminology:

# 자음 or jaeum:         consonant
# 모음 or moeum:         vowel
# 밭침 or batchim:       final letter
# 쌍받침 or ssangbatchim: double final letter
# 음절 or eumjeol:       block or syllable

# Hangul sorting order
# ㅏ ㅐ ㅑ ㅒ ㅓ ㅔ ㅕ ㅖ ㅗ ㅘ ㅙ ㅚ ㅛ ㅜ ㅝ ㅞ ㅟ ㅠ ㅡ ㅢ ㅣ
# ㄱ ㄲ ㄴ ㄷ ㄸ ㄹ ㄹㄹ ㅁ ㅂ ㅃ ㅅ ㅆ ㅇ ㅈ ㅉ ㅊ ㅋ ㅌ ㅍ ㅎ
# ㄱ ㄲ ㄳ ㄴ ㄵ ㄶ ㄷ ㄹ ㄺ ㄻ ㄼ ㄽ ㄾ ㄿ ㅀ ㅁ ㅂ ㅄ ㅅ ㅆ ㅇ ㅈ ㅊ ㅋ ㅌ ㅍ ㅎ


class HangulRomanizer:
    """Class for romanization from Hangul to Latin"""

    def __init__(self):
        # Initials
        jaeum = {
            "ㄱ": "g",
            "ㄲ": "kk",
            "ㄴ": "n",
            "ㄷ": "d",
            "ㄸ": "tt",
            "ㄹ": "r",
            "ㄹㄹ": "l",
            "ㅁ": "m",
            "ㅂ": "b",
            "ㅃ": "pp",
            "ㅅ": "s",
            "ㅆ": "ss",
            "ㅇ": "",
            "ㅈ": "j",
            "ㅉ": "jj",
            "ㅊ": "ch",
            "ㅋ": "k",
            "ㅌ": "t",
            "ㅍ": "p",
            "ㅎ": "h",
        }

        # Vowels
        moeum = {
            "ㅏ": "a",
            "ㅐ": "ae",
            "ㅑ": "ya",
            "ㅒ": "yae",
            "ㅓ": "eo",
            "ㅔ": "e",
            "ㅕ": "yeo",
            "ㅖ": "ye",
            "ㅗ": "o",
            "ㅘ": "wa",
            "ㅙ": "wae",
            "ㅚ": "oe",
            "ㅛ": "yo",
            "ㅜ": "u",
            "ㅝ": "wo",
            "ㅞ": "we",
            "ㅟ": "wi",
            "ㅠ": "yu",
            "ㅡ": "eu",
            "ㅢ": "ui",
            "ㅣ": "i",
        }

        # Final consonant
        batchim = {
            "ㄱ": "k",
            "ㄲ": "k",
            "ㄳ": "gs",
            "ㄴ": "n",
            "ㄵ": "nch",
            "ㄶ": "nh",
            "ㄷ": "t",
            "ㄹ": "l",
            "ㄺ": "lg",
            "ㄻ": "lm",
            "ㄼ": "lb",
            "ㄽ": "ls",
            "ㄾ": "lt",
            "ㄿ": "lp",
            "ㅀ": "lh",
            "ㅁ": "m",
            "ㅂ": "p",
            "ㅄ": "ps",
            "ㅅ": "t",
            "ㅆ": "t",
            "ㅇ": "ng",
            "ㅈ": "t",
            "ㅊ": "t",
            "ㅋ": "k",
            "ㅌ": "t",
            "ㅍ": "p",
            "ㅎ": "t",
        }

        # Final double consonant
        ssangbatchim = {
            "ㄳ": ("ㄱ", "ㅅ"),
            "ㄵ": ("ㄴ", "ㅈ"),
            "ㄶ": ("ㄴ", "ㅎ"),
            "ㄺ": ("ㄹ", "ㄱ"),
            "ㄻ": ("ㄹ", "ㅁ"),
            "ㄼ": ("ㄹ", "ㅂ"),
            "ㄽ": ("ㄹ", "ㅅ"),
            "ㄾ": ("ㄹ", "ㅌ"),
            "ㄿ": ("ㄹ", "ㅍ"),
            "ㅀ": ("ㄹ", "ㅎ"),
            "ㅄ": ("ㅂ", "ㅅ"),
        }

        self.__hangul = {
            "jaeum": jaeum,
            "moeum": moeum,
            "batchim": batchim,
            "ssangbatchim": ssangbatchim,
        }

        self.hangul = self.__hangul

    def __get_initial_next(self, syllables, i):
        """Get the initial letter of the next syllable of a word

        :param syllabes: list; syllables in Hangul
        :param i: int; the current index of the syllable in the sentence"""
        if i < (len(syllables) - 1):
            if syllables[i + 1] != "" and is_hangul(syllables[i + 1]):
                return get_initial(syllables[i + 1])

        return ""

    def __get_final_prior(self, syllables, i):
        """Get the batchim of the prior syllable of a word

        :param syllabes: list; syllables in Hangul
        :param i: int; the current index of the syllable in the sentence"""
        if i > 0:
            if syllables[i - 1] != "" and is_hangul(syllables[i - 1]):
                return get_final(syllables[i - 1])

        return ""

    def is_ssangbatchim(self, batchim):
        """Return True if the batchim is double batchim"""

        return batchim in self.__hangul["ssangbatchim"]

    def has_ssangbatchim(self, syllable):
        """Return True if the syllable contains a double batchim"""

        if is_hangul(syllable):
            return self.is_ssangbatchim(get_final(syllable))
        else:
            return False

    def split_ssangbatchim(self, char):
        """Split the double batchim in a tuple"""

        if char in self.__hangul["ssangbatchim"]:
            return self.__hangul["ssangbatchim"].get(char)
        else:
            return self.__hangul["ssangbatchim"].get(get_final(char))

    def jaeum(self, syllable, prior=""):
        """Convert a consonant to latin script following grammatical rules"""

        if syllable in self.__hangul["jaeum"]:
            current = syllable
        else:
            current = get_initial(syllable)

        if prior in ("ㄴ", "ㄹ"):
            if current == "ㄹ":
                return self.__hangul["jaeum"].get("ㄹㄹ")

        elif prior in ("ㄶ", "ㅀ", "ㅎ"):
            if current == "ㄱ":
                return self.__hangul["jaeum"].get("ㅋ")
            elif current == "ㄷ":
                return self.__hangul["jaeum"].get("ㅌ")
            elif current == "ㅂ":
                return self.__hangul["jaeum"].get("ㅍ")
        elif current == "ㅎ":
            if prior in ["ㄷ", "ㅅ", "ㅆ", "ㅈ", "ㅊ", "ㅌ"]:
                return ""

        return self.__hangul["jaeum"].get(current)

    def moeum(self, syllable):
        """Convert a vowel to latin script"""

        if syllable in self.__hangul["moeum"]:
            return self.__hangul["moeum"].get(syllable)
        else:
            return self.__hangul["moeum"].get(get_vowel(syllable))

    def batchim(self, syllable, next=""):
        """Convert a final consonant to latin script following grammatical rules"""

        current = get_final(syllable)

        if current == "":
            return ""

        # ㅇ comes first because it's a special case
        if next != "":
            if next == "ㅇ":
                if current == "ㅇ":
                    pass
                elif current in self.__hangul["jaeum"]:
                    return self.jaeum(current)
            elif self.is_ssangbatchim(current):
                return self.batchim(self.split_ssangbatchim(current)[0])

            elif next in ("ㄴ", "ㅁ"):
                if current == "ㅂ":
                    return self.jaeum("ㅁ")

            elif next in ("ㄱ", "ㄷ", "ㅂ"):
                if current == "ㅎ":
                    return ""

            elif next == "ㄹ":
                if current in ("ㄴ", "ㄹ"):
                    return self.jaeum("ㄹㄹ")
            elif next == "ㅎ":
                if current == "ㄱ":
                    return self.jaeum("ㅋ")
                if current == "ㄷ":
                    return self.jaeum("ㅌ")
                if current == "ㅂ":
                    return self.jaeum("ㅍ")

        return self.__hangul["batchim"].get(current)

    def has_hangul(self, string):
        """Return whether there is any hangul character in the text."""
        return any(is_hangul(syllable) for syllable in string)

    def romanize(self, string):
        """Convert a string from Hangul to Latin Script"""

        if not self.has_hangul(string):
            return string

        sentence_latin = ""
        syllables = list(string)

        for i, syllable in enumerate(syllables):
            if is_hangul(syllable):
                sentence_latin += self.jaeum(
                    syllable, self.__get_final_prior(syllables, i)
                )
                sentence_latin += self.moeum(syllable)
                sentence_latin += self.batchim(
                    syllable, self.__get_initial_next(syllables, i)
                )
            else:
                sentence_latin += syllable

        sentence_latin = sentence_latin.strip()

        if (
            sentence_latin
            and not sentence_latin[0].isupper()
            and sentence_latin[0].isalpha()
        ):
            sentence_latin = sentence_latin.capitalize()

        return sentence_latin
