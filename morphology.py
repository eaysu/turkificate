"""Small, deterministic helpers for Turkish suffix harmony.

The normalizer is deliberately not a general Turkish morphological analyser.
These helpers cover the productive suffixes that commonly follow numbers and
semiotic expressions (``5 TL'lik``, ``09:30'da`` and ``3 kg'dan``).
"""

from __future__ import annotations

import re

_VOWELS = "aeıioöuü"
_FRONT = "eiöü"
_ROUNDED = "ouöü"
_VOICELESS = "fstkçşhp"
# Numeral tails are the main callers here: ``üçü`` keeps ç, while ``dördü``
# and ``kitabı`` use the productive t/p/k changes.
_SOFTEN = {"p": "b", "t": "d", "k": "ğ"}


def _lower(text: str) -> str:
    return text.replace("I", "ı").replace("İ", "i").lower()


def _last_vowel(word: str) -> str:
    for char in reversed(_lower(word)):
        if char in _VOWELS:
            return char
    return "a"


def _low_vowel(word: str) -> str:
    return "e" if _last_vowel(word) in _FRONT else "a"


def _high_vowel(word: str) -> str:
    vowel = _last_vowel(word)
    if vowel in "aı":
        return "ı"
    if vowel in "ei":
        return "i"
    if vowel in "ou":
        return "u"
    return "ü"


def _ends_vowel(word: str) -> bool:
    return bool(word) and _lower(word[-1]) in _VOWELS


def _softened(word: str) -> str:
    """Soften a final consonant before a vowel where the common rule applies."""
    if word and _lower(word[-1]) in _SOFTEN:
        return word[:-1] + _SOFTEN[_lower(word[-1])]
    return word


def _family(suffix: str) -> str | None:
    suffix = _lower(suffix)
    if suffix in {"inci", "ıncı", "uncu", "üncü", "nci", "ncı", "ncu", "ncü"}:
        return "ordinal"
    if suffix in {"lik", "lık", "luk", "lük"}:
        return "derivation"
    if suffix in {"de", "da", "te", "ta"}:
        return "locative"
    if suffix in {"den", "dan", "ten", "tan"}:
        return "ablative"
    if suffix in {"e", "a", "ye", "ya"}:
        return "dative"
    if suffix in {"i", "ı", "u", "ü", "yi", "yı", "yu", "yü"}:
        return "accusative"
    if suffix in {"in", "ın", "un", "ün", "nin", "nın", "nun", "nün"}:
        return "genitive"
    return None


def inflect_tail(phrase: str, source_suffix: str | None) -> str:
    """Attach the equivalent productive suffix to the final word in *phrase*.

    Unknown suffixes are retained with their apostrophe rather than guessed.
    This keeps the normalizer conservative for forms outside its bounded scope.
    """
    if not source_suffix:
        return phrase
    family = _family(source_suffix)
    if family is None:
        return f"{phrase}'{source_suffix}"

    match = re.search(r"(\S+)$", phrase)
    if match is None:
        return phrase
    prefix, tail = phrase[:match.start()], match.group(1)
    vowel = _ends_vowel(tail)
    low, high = _low_vowel(tail), _high_vowel(tail)
    stop = "t" if _lower(tail[-1]) in _VOICELESS else "d"

    if family == "ordinal":
        addition = f"n{high}" if vowel else f"{high}nc{high}"
    elif family == "derivation":
        addition = f"l{high}k"
    elif family == "locative":
        addition = f"{stop}{low}"
    elif family == "ablative":
        addition = f"{stop}{low}n"
    elif family == "dative":
        tail = _softened(tail)
        addition = f"y{low}" if vowel else low
    elif family == "accusative":
        tail = _softened(tail)
        addition = f"y{high}" if vowel else high
    else:  # genitive
        tail = _softened(tail)
        addition = f"n{high}n" if vowel else f"{high}n"
    return prefix + tail + addition
