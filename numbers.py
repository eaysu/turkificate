"""Turkish number-to-words engine.

This is the core of the library: it converts integers, decimals, signed numbers
and ordinals into their written Turkish form according to Turkish grammar.

Turkish-specific rules handled here:
- 100 = "yüz" (NOT "bir yüz"), 1000 = "bin" (NOT "bir bin")
- 1,000,000 = "bir milyon" (million and above keep the leading "bir")
- The decimal separator is a comma: 3,14 -> "üç virgül on dört"
- The thousands separator is a dot: 1.234.567 -> "bir milyon iki yüz otuz dört bin ..."
- Ordinals follow 4-way vowel harmony and consonant softening (dört -> dördüncü)

Note: the produced words are intentionally Turkish — that is the library's output.
"""

from functools import lru_cache

__all__ = [
    "integer_to_words",
    "integer_to_ordinal",
    "read_number",
    "number_to_words",
]

_ONES = ["", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
_TENS = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]
# Scale words (powers of 1000). Extending this list automatically supports larger numbers.
_SCALES = ["", "bin", "milyon", "milyar", "trilyon", "katrilyon", "kentilyon"]

_VOWELS = "aeıioöuü"


def _three_digits(n):
    """Convert a number in 0..999 to a list of word parts."""
    parts = []
    h, rem = divmod(n, 100)
    t, o = divmod(rem, 10)
    if h:
        if h != 1:                # "bir yüz" is never said, just "yüz"
            parts.append(_ONES[h])
        parts.append("yüz")
    if t:
        parts.append(_TENS[t])
    if o:
        parts.append(_ONES[o])
    return parts


@lru_cache(maxsize=4096)
def integer_to_words(n: int) -> str:
    """Convert an integer to its written Turkish form.

    >>> integer_to_words(0)
    'sıfır'
    >>> integer_to_words(1234567)
    'bir milyon iki yüz otuz dört bin beş yüz altmış yedi'
    """
    if n == 0:
        return "sıfır"

    negative = n < 0
    n = abs(n)

    groups = []                   # groups of three digits, least significant first
    while n > 0:
        n, g = divmod(n, 1000)
        groups.append(g)

    if len(groups) > len(_SCALES):
        raise ValueError("Number exceeds the largest supported scale.")

    parts = []
    for i in range(len(groups) - 1, -1, -1):
        g = groups[i]
        if g == 0:
            continue
        if i == 1 and g == 1:     # "bir bin" is never said, just "bin"
            parts.append("bin")
            continue
        parts.extend(_three_digits(g))
        if i > 0:
            parts.append(_SCALES[i])

    words = " ".join(parts)
    return "eksi " + words if negative else words


def _last_vowel(word: str):
    for ch in reversed(word):
        if ch in _VOWELS:
            return ch
    return None


def _ordinal_suffix(word: str) -> str:
    """Return the correct ordinal suffix based on the word's last vowel."""
    lv = _last_vowel(word)
    ends_with_vowel = word[-1] in _VOWELS
    # 4-way vowel harmony: (full form, reduced form for vowel-ending stems)
    table = {
        "a": ("ıncı", "ncı"), "ı": ("ıncı", "ncı"),
        "e": ("inci", "nci"), "i": ("inci", "nci"),
        "o": ("uncu", "ncu"), "u": ("uncu", "ncu"),
        "ö": ("üncü", "ncü"), "ü": ("üncü", "ncü"),
    }
    full, reduced = table.get(lv, ("ıncı", "ncı"))
    return reduced if ends_with_vowel else full


def integer_to_ordinal(n: int) -> str:
    """Convert an integer to its Turkish ordinal form.

    >>> integer_to_ordinal(1)
    'birinci'
    >>> integer_to_ordinal(4)
    'dördüncü'
    >>> integer_to_ordinal(100)
    'yüzüncü'
    """
    words = integer_to_words(n).split()
    last = words[-1]
    if last == "dört":            # consonant softening: t -> d
        last = "dörd"
    words[-1] = last + _ordinal_suffix(last)
    return " ".join(words)


def _read_fraction(frac: str) -> str:
    """Read the part after the comma. Leading zeros are read as 'sıfır'."""
    stripped = frac.lstrip("0")
    lead_zeros = len(frac) - len(stripped)
    parts = ["sıfır"] * lead_zeros
    if stripped:
        parts.append(integer_to_words(int(stripped)))
    elif lead_zeros == 0:
        parts.append("sıfır")
    return " ".join(parts)


def read_number(token: str) -> str:
    """Convert a Turkish-formatted numeric string to words.

    The thousands separator is '.' and the decimal separator is ','.

    >>> read_number("1.234,5")
    'bin iki yüz otuz dört virgül beş'
    >>> read_number("-3,05")
    'eksi üç virgül sıfır beş'
    """
    token = token.strip()
    if not token:
        return ""

    sign = ""
    if token[0] in "+-":
        if token[0] == "-":
            sign = "eksi "
        token = token[1:]

    if "," in token:
        int_part, frac_part = token.split(",", 1)
    else:
        int_part, frac_part = token, None

    int_part = int_part.replace(".", "")        # drop thousands separators
    words = integer_to_words(int(int_part)) if int_part else "sıfır"

    if frac_part:
        words = f"{words} virgül {_read_fraction(frac_part)}"

    return (sign + words).strip()


def number_to_words(value) -> str:
    """General-purpose entry point: accepts an int or a numeric string."""
    if isinstance(value, int):
        return integer_to_words(value)
    return read_number(str(value))
