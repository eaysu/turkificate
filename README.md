# turkificate

A Turkish text normalization library. It converts numbers, dates, times,
abbreviations, currencies, percentages, ordinals and symbols into their written
Turkish form, following Turkish grammar. Built for TTS pre-processing, search
indexing and text cleaning.

> _"The language is the core of our being - Noam Chomsky"_ 

No external dependencies — pure standard library.

## Installation

```bash
pip install turkificate
```

Or from a local checkout:

```bash
pip install -e .
```

## Quick start

```python
import turkificate

turkificate.turkificate("Dr. Ahmet 15.03.2024'te %25 indirimle 1.250 TL ödedi.")
# "doktor Ahmet on beş Mart iki bin yirmi dört'te yüzde yirmi beş
#  indirimle bin iki yüz elli lira ödedi."
```

`turkificate()` is the main function; `normalize()` is a kept alias for the same call.

> The **output** is intentionally Turkish (e.g. `yüz`, `bin`, `Mart`) — that is the
> whole point of the library. Only the **code, API and docs** are in English.

## Selecting concepts

```python
from turkificate import TurkishNormalizer

tn = TurkishNormalizer(features=["numbers", "dates"])
tn.normalize("Saat 14:30, fiyat 99,90 TL")
# "Saat 14:30, fiyat doksan dokuz virgül doksan TL"  (times & currency untouched)
```

### Normalize everything

Pass nothing (the default), or the explicit `"all"` keyword:

```python
TurkishNormalizer()                          # all concepts (default)
TurkishNormalizer(features="all")            # all concepts
TurkishNormalizer(features=["all"])          # all concepts
TurkishNormalizer(features=turkificate.ALL)  # all concepts
```

List available concepts with `turkificate.available_features()`.

| Concept | Description | Example |
|---|---|---|
| `numbers` | integer / decimal / signed | `3,5` → üç virgül beş |
| `dates` | DD.MM.YYYY | `15.03.2024` → on beş Mart iki bin yirmi dört |
| `times` | HH:MM(:SS) | `14:30` → on dört otuz |
| `percent` | percent sign | `%50` → yüzde elli |
| `currency` | currencies | `100 TL` → yüz lira |
| `ordinals` | ordinal numbers | `5'inci` → beşinci |
| `units` | units of measure | `42 km` → kırk iki kilometre |
| `abbreviations` | lexical abbreviations | `Dr.` → doktor |
| `symbols` | single-character symbols | `&` → ve |
| `whitespace` | whitespace cleanup | (always the final step) |

## Per-concept options

```python
tn = TurkishNormalizer(options={
    "times": {"prefix_hour": True},        # 09:05 → "saat dokuz beş"
    "ordinals": {"period_ordinals": True}, # "3. kat" → "üçüncü kat"
})
```

## Per-concept helpers

```python
turkificate.normalize_numbers("3 elma")     # "üç elma"
turkificate.normalize_dates(...)
turkificate.normalize_currency(...)
# normalize_times, normalize_percent, normalize_ordinals,
# normalize_units, normalize_abbreviations, normalize_symbols
```

Direct number engine:

```python
from turkificate import integer_to_words, integer_to_ordinal, read_number
integer_to_words(1_000_000)   # "bir milyon"
integer_to_ordinal(4)         # "dördüncü"
read_number("1.234,5")        # "bin iki yüz otuz dört virgül beş"
```

## Adding a new concept

Subclass `Normalizer` and register it with `@register`:

```python
from turkificate import Normalizer, register
import re

@register
class EmojiNormalizer(Normalizer):
    name = "emoji"

    def configure(self, **opts):
        self._re = re.compile(r":\)")

    def apply(self, text):
        return self._re.sub("gülen yüz", text)
```

It is now usable via `TurkishNormalizer(features=["emoji", ...])` or `"all"`.

## Architecture

- **Strategy** — each concept is an independent class with a common `Normalizer` interface.
- **Pipeline (Chain)** — normalizers run in order; number-bearing concepts run before the bare `numbers` concept to avoid double conversion.
- **Registry + Facade** — concepts are selected by name; `TurkishNormalizer` composes them.

Optimization: every regex is compiled once in the constructor; the abbreviation,
unit and currency dictionaries are compiled into a single alternation regex; the
number-to-words engine is `lru_cache`-d; and because `apply` is pure, a single
instance is reused across thousands of calls.

## Known limits (roadmap)

- The period ordinal form (`3.`) is disabled by default because it clashes with a sentence-final period; enable it with `period_ordinals=True`.
- The number engine is one-way; the reverse direction (words → digits) is not yet implemented.
- Context-sensitive suffixes (`5'te` → "beşte") are not handled yet.
- Roman numerals, phone numbers and fractions (`3/4`) can be added.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Publishing

This repo ships a GitHub Actions workflow (`.github/workflows/publish.yml`) that
publishes to PyPI via Trusted Publishing (no API tokens) when you create a
GitHub Release. See the project README section below or the PyPI docs on
trusted publishers.

## License

MIT — see [LICENSE](LICENSE).
