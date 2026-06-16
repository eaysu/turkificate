"""Concrete normalizers (Strategy implementations).

Ordering note: concepts that contain numbers (percent, currency, dates, times,
ordinals, units) run BEFORE the bare ``numbers`` normalizer and already convert
their own digits, so no double conversion happens.
Email/URL normalizers run first so the symbol normalizer never sees raw @ or dots.
"""

import re

from .base import Normalizer, register
from .data import (
    ABBREVIATIONS,
    COMPANIES,
    CURRENCY,
    MONTHS,
    SYMBOLS,
    TECHNOLOGY_TERMS,
    UNITS,
)
from .numbers import integer_to_ordinal, integer_to_words, read_number

_TRAIL_PUNCT = re.compile(r'[.,;:!?)]+$')
_DIGIT_WORDS = [integer_to_words(i) for i in range(10)]


@register
class EmailNormalizer(Normalizer):
    """Convert email addresses to spoken form: info@firma.com -> info et firma nokta com."""

    name = "emails"

    def configure(self, **options):
        self._re = re.compile(r'[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+')

    def apply(self, text):
        def repl(m):
            local, domain = m.group(0).split('@', 1)
            local = (local
                     .replace('.', ' nokta ')
                     .replace('+', ' artı ')
                     .replace('-', ' tire ')
                     .replace('_', ' alt çizgi '))
            domain = domain.replace('.', ' nokta ').replace('-', ' tire ')
            return re.sub(r' +', ' ', f"{local.strip()} et {domain.strip()}")
        return self._re.sub(repl, text)


@register
class UrlNormalizer(Normalizer):
    """Convert URLs to spoken form: https://firma.com/detay -> firma nokta com bölü detay."""

    name = "urls"

    def configure(self, **options):
        self._re = re.compile(r'https?://\S+|www\.\S+')

    def apply(self, text):
        def repl(m):
            url = m.group(0)
            trail_m = _TRAIL_PUNCT.search(url)
            trail = trail_m.group(0) if trail_m else ''
            if trail:
                url = url[:-len(trail)]
            for prefix in ('https://', 'http://', 'www.'):
                if url.startswith(prefix):
                    url = url[len(prefix):]
                    break
            url = (url
                   .replace('.', ' nokta ')
                   .replace('/', ' bölü ')
                   .replace('-', ' tire ')
                   .replace('_', ' alt çizgi '))
            return re.sub(r' +', ' ', url).strip() + trail
        return self._re.sub(repl, text)


def _digits_only(value):
    return re.sub(r"\D", "", value)


def _read_digits(value):
    return " ".join(_DIGIT_WORDS[int(ch)] for ch in value)


def _normalize_phone_digits(value):
    digits = _digits_only(value)
    if digits.startswith("0090"):
        digits = digits[4:]
    if digits.startswith("90") and len(digits) == 12:
        digits = digits[2:]
    if digits.startswith("0"):
        digits = digits[1:]
    if len(digits) != 10 or digits[0] not in "2345":
        return None
    return digits


def _read_phone_number(value):
    digits = _normalize_phone_digits(value)
    if digits is None:
        return None
    area, first, second, third = digits[:3], digits[3:6], digits[6:8], digits[8:]
    groups = ["sıfır", area, first, second, third]
    return " ".join(integer_to_words(int(group)) if group != "sıfır" else group
                    for group in groups)


def _is_valid_turkish_id(value):
    digits = _digits_only(value)
    if len(digits) != 11 or digits[0] == "0":
        return False
    nums = [int(ch) for ch in digits]
    odd_sum = sum(nums[i] for i in (0, 2, 4, 6, 8))
    even_sum = sum(nums[i] for i in (1, 3, 5, 7))
    tenth = ((odd_sum * 7) - even_sum) % 10
    eleventh = sum(nums[:10]) % 10
    return nums[9] == tenth and nums[10] == eleventh


@register
class PhoneNormalizer(Normalizer):
    """Convert Turkish phone numbers to spoken form: 0532 123 45 67 -> sıfır beş yüz otuz iki ..."""

    name = "phones"

    def configure(self, **options):
        self._re = re.compile(
            r"(?<![\w+])"
            r"(?:(?:\+90|0090|90)[\s.-]*)?"
            r"\(?(0?[2-5]\d{2})\)?[\s.-]*"
            r"(\d{3})[\s.-]*(\d{2})[\s.-]*(\d{2})"
            r"(?!\d)"
        )

    def apply(self, text):
        def repl(m):
            spoken = _read_phone_number(m.group(0))
            return spoken if spoken is not None else m.group(0)
        return self._re.sub(repl, text)


@register
class TurkishIdNormalizer(Normalizer):
    """Convert valid Turkish identity numbers to digit-by-digit spoken form."""

    name = "turkish_ids"

    def configure(self, **options):
        self._re = re.compile(r"(?<![\d+])([1-9](?:[\s.-]?\d){10})(?!\d)")

    def apply(self, text):
        def repl(m):
            value = m.group(1)
            if not _is_valid_turkish_id(value):
                return m.group(0)
            return _read_digits(_digits_only(value))
        return self._re.sub(repl, text)


@register
class CompanyNormalizer(Normalizer):
    """Convert company and brand names to Turkish TTS spoken forms."""

    name = "companies"

    def configure(self, **options):
        keys = sorted(COMPANIES, key=len, reverse=True)
        alt = "|".join(re.escape(k).replace(r"\ ", r"\s+") for k in keys)
        self._re = re.compile(rf"(?<!\w)({alt})(?!\w)", re.IGNORECASE)

    def apply(self, text):
        def repl(m):
            key = re.sub(r"\s+", " ", m.group(1).lower())
            return COMPANIES[key]

        return self._re.sub(repl, text)


@register
class TechnologyTermNormalizer(Normalizer):
    """Convert technology acronyms and product terms to Turkish TTS spoken forms."""

    name = "technology_terms"

    def configure(self, **options):
        keys = sorted(TECHNOLOGY_TERMS, key=len, reverse=True)
        alt = "|".join(re.escape(k) for k in keys)
        self._re = re.compile(rf"(?<!\w)({alt})(?!\w)")

    def apply(self, text):
        return self._re.sub(lambda m: TECHNOLOGY_TERMS[m.group(1)], text)

# Turkish-formatted number pattern (thousands '.', decimal ','). Reused widely.
_NUM = r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?"


@register
class NumberNormalizer(Normalizer):
    """Convert bare numbers (integer / decimal / signed) to words."""

    name = "numbers"

    def configure(self, **options):
        # A sign is only read when it is not in the middle of a token (3-5 = a range).
        self._re = re.compile(rf"(?<![\w.,])([+-]?)({_NUM})")

    def apply(self, text):
        def repl(m):
            return read_number(m.group(1) + m.group(2))
        return self._re.sub(repl, text)


@register
class OrdinalNormalizer(Normalizer):
    """Convert ordinals: 3'üncü -> üçüncü (apostrophe form), 3. -> üçüncü (period form).

    The period form requires whitespace + a non-whitespace char after the dot,
    so sentence-final periods are not affected.
    Disable with ``period_ordinals=False``.
    """

    name = "ordinals"

    def configure(self, period_ordinals: bool = True, **options):
        self._apos = re.compile(
            r"(?<!\d)(\d+)['’](?:inci|ıncı|uncu|üncü|nci|ncı|ncu|ncü)\b",
            re.IGNORECASE,
        )
        # Period form: only on a digit-dot-space-word pattern (not at end of sentence).
        self._dot = re.compile(r"(?<!\d)(\d+)\.(?=\s+\S)") if period_ordinals else None

    def apply(self, text):
        text = self._apos.sub(lambda m: integer_to_ordinal(int(m.group(1))), text)
        if self._dot:
            text = self._dot.sub(lambda m: integer_to_ordinal(int(m.group(1))), text)
        return text


@register
class DateNormalizer(Normalizer):
    """DD.MM.YYYY / DD/MM/YYYY / DD-MM-YYYY -> 'on beş Mart iki bin yirmi dört'."""

    name = "dates"

    def configure(self, **options):
        self._re = re.compile(r"(?<!\d)(\d{1,2})[./-](\d{1,2})[./-](\d{4})(?!\d)")

    def apply(self, text):
        def repl(m):
            day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if not (1 <= day <= 31 and 1 <= month <= 12):
                return m.group(0)        # invalid date: leave untouched
            return f"{integer_to_words(day)} {MONTHS[month]} {integer_to_words(year)}"
        return self._re.sub(repl, text)


@register
class TimeNormalizer(Normalizer):
    """HH:MM(:SS) -> 'on dört otuz'. ``prefix_hour=True`` prepends the word 'saat'."""

    name = "times"

    def configure(self, prefix_hour: bool = False, **options):
        self._prefix_hour = prefix_hour
        self._re = re.compile(r"(?<!\d)([01]?\d|2[0-3]):([0-5]\d)(?::([0-5]\d))?(?!\d)")

    def apply(self, text):
        def repl(m):
            parts = []
            if self._prefix_hour:
                parts.append("saat")
            parts.append(integer_to_words(int(m.group(1))))
            minutes = int(m.group(2))
            if minutes != 0:
                parts.append(integer_to_words(minutes))
            if m.group(3) is not None:
                parts.append(integer_to_words(int(m.group(3))))
            return " ".join(parts)
        return self._re.sub(repl, text)


@register
class PercentNormalizer(Normalizer):
    """In Turkish the percent sign is read BEFORE the number: %50 -> 'yüzde elli'."""

    name = "percent"

    def configure(self, **options):
        # %50, % 50 and 50% forms.
        self._pre = re.compile(rf"%\s*({_NUM})")
        self._post = re.compile(rf"({_NUM})\s*%")

    def apply(self, text):
        text = self._pre.sub(lambda m: f"yüzde {read_number(m.group(1))}", text)
        text = self._post.sub(lambda m: f"yüzde {read_number(m.group(1))}", text)
        return text


@register
class CurrencyNormalizer(Normalizer):
    """Convert currencies: 100 TL -> 'yüz lira', $50 -> 'elli dolar'."""

    name = "currency"

    def configure(self, **options):
        # Alphabetic codes (TL, USD...) almost always TRAIL the number in Turkish
        # ("100 TL", never "TL 100"); only symbols ($ € £ ₺) may lead a number.
        symbols = sorted((c for c in CURRENCY if not c.isalpha()), key=len, reverse=True)
        all_codes = sorted(CURRENCY, key=len, reverse=True)
        sym_alt = "|".join(re.escape(c) for c in symbols)
        all_alt = "|".join(re.escape(c) for c in all_codes)
        # Leading: symbols only ($50, ₺100).
        self._pre = re.compile(rf"({sym_alt})\s*({_NUM})")
        # Trailing: symbols or codes (100 TL, 100₺, 50$).
        self._post = re.compile(rf"({_NUM})\s*({all_alt})(?![a-zçğıöşü])", re.IGNORECASE)

    def apply(self, text):
        def pre(m):
            return f"{read_number(m.group(2))} {CURRENCY[m.group(1).lower()]}"

        def post(m):
            return f"{read_number(m.group(1))} {CURRENCY[m.group(2).lower()]}"

        # Trailing form first so codes attach to the number on their left.
        text = self._post.sub(post, text)
        text = self._pre.sub(pre, text)
        return text


@register
class UnitNormalizer(Normalizer):
    """Expand units (only after a number): 5 km -> '5 kilometre'.

    Only the unit word is expanded here; the digits themselves are converted by
    the ``numbers`` normalizer.
    """

    name = "units"

    def configure(self, **options):
        units = sorted(UNITS, key=len, reverse=True)
        alt = "|".join(re.escape(u) for u in units)
        # A unit right after a digit, not followed by another letter/digit.
        self._re = re.compile(rf"(?<=\d)\s*({alt})(?![a-zçğıöşü0-9])", re.IGNORECASE)

    def apply(self, text):
        def repl(m):
            key = m.group(1)
            expansion = UNITS.get(key.lower()) or UNITS.get(key)
            return f" {expansion}" if expansion else key
        return self._re.sub(repl, text)


@register
class AbbreviationNormalizer(Normalizer):
    """Expand lexical abbreviations: Dr. -> doktor, vb. -> ve benzeri."""

    name = "abbreviations"

    def configure(self, **options):
        keys = sorted(ABBREVIATIONS, key=len, reverse=True)
        alt = "|".join(re.escape(k) for k in keys)
        self._re = re.compile(rf"(?<!\w)({alt})", re.IGNORECASE)

    def apply(self, text):
        return self._re.sub(lambda m: ABBREVIATIONS[m.group(1).lower()], text)


@register
class SymbolNormalizer(Normalizer):
    """Convert single-character symbols: & -> ve, @ -> et, ° -> derece."""

    name = "symbols"

    def configure(self, **options):
        alt = "|".join(re.escape(s) for s in SYMBOLS)
        self._re = re.compile(rf"({alt})")

    def apply(self, text):
        return self._re.sub(lambda m: f" {SYMBOLS[m.group(1)]} ", text)


@register
class WhitespaceNormalizer(Normalizer):
    """Final cleanup: collapse extra whitespace, drop spaces before punctuation."""

    name = "whitespace"

    def configure(self, **options):
        self._multi = re.compile(r"\s+")
        self._before_punct = re.compile(r"\s+([,.!?;:])")

    def apply(self, text):
        text = self._before_punct.sub(r"\1", text)
        return self._multi.sub(" ", text).strip()
