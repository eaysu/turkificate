"""turkificate — a Turkish text normalization library.

Quick start
-----------
>>> import turkificate
>>> turkificate.turkificate("Dr. Ahmet 15.03.2024'te %25 indirimle 1.250 TL ödedi.")
"doktor Ahmet on beş Mart iki bin yirmi dörtte yüzde yirmi beş indirimle bin iki yüz elli lira ödedi."

``turkificate()`` is the main function; ``normalize()`` is a kept alias.

Selecting concepts
-------------------
>>> tn = turkificate.TurkishNormalizer(features=["numbers", "dates"])
>>> tn.normalize("Saat 14:30, fiyat 99,90 TL")   # times and currency untouched
'Saat 14:30, fiyat doksan dokuz virgül doksan TL'

Normalize everything (default, or explicit "all")
-------------------------------------------------
>>> turkificate.TurkishNormalizer(features="all").normalize("%50")
'yüzde elli'

Per-concept helpers
-------------------
>>> turkificate.normalize_numbers("3 kişi geldi")
'üç kişi geldi'
"""

from .base import Normalizer, available_features, get_registry, register
from .numbers import (
    integer_to_ordinal,
    integer_to_words,
    number_to_words,
    read_number,
)
from .pipeline import ALL, DEFAULT_ORDER, Pipeline, TurkishNormalizer
from .results import NormalizationAmbiguityError, NormalizationIssue, NormalizationResult

__version__ = "0.2.0"

__all__ = [
    # Main interface
    "TurkishNormalizer",
    "Pipeline",
    "turkificate",
    "normalize",
    "normalize_with_lexicon",
    "DEFAULT_ORDER",
    "ALL",
    "NormalizationResult",
    "NormalizationIssue",
    "NormalizationAmbiguityError",
    # Number engine
    "integer_to_words",
    "integer_to_ordinal",
    "read_number",
    "number_to_words",
    # Extension
    "Normalizer",
    "register",
    "get_registry",
    "available_features",
    # Per-concept helpers
    "normalize_emails",
    "normalize_urls",
    "normalize_phones",
    "normalize_turkish_ids",
    "normalize_companies",
    "normalize_technology_terms",
    "normalize_ibans",
    "normalize_numbers",
    "normalize_dates",
    "normalize_times",
    "normalize_percent",
    "normalize_currency",
    "normalize_fractions",
    "normalize_ranges",
    "normalize_ordinals",
    "normalize_roman_numerals",
    "normalize_units",
    "normalize_abbreviations",
    "normalize_symbols",
]

# Default, reusable instance covering every concept.
_default = TurkishNormalizer()


def turkificate(text: str) -> str:
    """Normalize Turkish text using every available concept (the main function)."""
    return _default.normalize(text)


# Kept alias for readability / discoverability.
normalize = turkificate


def normalize_with_lexicon(text: str, lexicon: dict[str, str]) -> str:
    """Normalize text with caller-owned source-to-pronunciation overrides."""
    return TurkishNormalizer(lexicon=lexicon).normalize(text)


def _make_single(feature):
    """Build a cached helper that runs a single concept."""
    holder = {}

    def fn(text: str) -> str:
        tn = holder.get("tn")
        if tn is None:
            tn = holder["tn"] = TurkishNormalizer(features=[feature])
        return tn.normalize(text)

    fn.__name__ = f"normalize_{feature}"
    fn.__doc__ = f"Normalize only the '{feature}' concept."
    return fn


normalize_emails = _make_single("emails")
normalize_urls = _make_single("urls")
normalize_phones = _make_single("phones")
normalize_turkish_ids = _make_single("turkish_ids")
normalize_companies = _make_single("companies")
normalize_technology_terms = _make_single("technology_terms")
normalize_ibans = _make_single("ibans")
normalize_numbers = _make_single("numbers")
normalize_dates = _make_single("dates")
normalize_times = _make_single("times")
normalize_percent = _make_single("percent")
normalize_currency = _make_single("currency")
normalize_fractions = _make_single("fractions")
normalize_ranges = _make_single("ranges")
normalize_ordinals = _make_single("ordinals")
normalize_roman_numerals = _make_single("roman_numerals")
normalize_units = _make_single("units")
normalize_abbreviations = _make_single("abbreviations")
normalize_symbols = _make_single("symbols")
