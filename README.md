# turkificate

A Turkish text normalization library. It converts numbers, dates, times,
phone numbers, Turkish identity numbers, company names, technology terms,
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

Enable or disable company/brand name normalization through the same feature list:

```python
TurkishNormalizer(features=["companies"]).normalize("Turkcell ve Vodafone")
# "türksel ve vodafon"

TurkishNormalizer(features=["companies"]).normalize("Google, Apple ve Microsoft")
# "gugıl, epıl ve maykrosoft"

TurkishNormalizer(features=["currency"]).normalize("Turkcell 100 TL")
# "Turkcell yüz lira"  (company names untouched)
```

Technology term normalization is also selectable:

```python
TurkishNormalizer(features=["technology_terms"]).normalize("GPT, FP16 ve API")
# "ci pi ti, ef pi on altı ve ey pi ay"

TurkishNormalizer(features=["numbers"]).normalize("GPT ve 2")
# "GPT ve iki"  (technology terms untouched)
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
| `emails` | e-mail addresses | `info@firma.com` → info et firma nokta com |
| `urls` | URLs | `https://firma.com/detay` → firma nokta com bölü detay |
| `phones` | Turkish phone numbers | `0532 123 45 67` → sıfır beş yüz otuz iki yüz yirmi üç kırk beş altmış yedi |
| `turkish_ids` | valid Turkish identity numbers | `10000000146` → bir sıfır sıfır sıfır sıfır sıfır sıfır sıfır bir dört altı |
| `companies` | company and brand names | `Google` → gugıl, `Garanti BBVA` → Garanti bebevea |
| `technology_terms` | AI, ML and common technology terms | `GPT` → ci pi ti, `FP16` → ef pi on altı |
| `numbers` | integer / decimal / signed | `3,5` → üç virgül beş |
| `dates` | DD.MM.YYYY | `15.03.2024` → on beş Mart iki bin yirmi dört |
| `times` | HH:MM(:SS) | `14:30` → on dört otuz |
| `percent` | percent sign | `%50` → yüzde elli |
| `currency` | currencies | `100 TL` → yüz lira |
| `ordinals` | ordinal numbers | `5'inci` → beşinci, `3. kat` → üçüncü kat |
| `units` | units of measure | `42 km` → kırk iki kilometre, `-3 °C` → eksi üç derece |
| `abbreviations` | lexical abbreviations | `Dr.` → doktor |
| `symbols` | single-character symbols | `&` → ve, `×` → çarpı, `÷` → bölü |
| `whitespace` | whitespace cleanup | (always the final step) |

## Per-concept options

```python
tn = TurkishNormalizer(options={
    "times":   {"prefix_hour":     True},  # 09:05 → "saat dokuz beş"
    "ordinals": {"period_ordinals": False}, # disable "3. kat" → "üçüncü kat" (on by default)
})
```

## Per-concept helpers

```python
turkificate.normalize_numbers("3 elma")               # "üç elma"
turkificate.normalize_emails("info@firma.com")         # "info et firma nokta com"
turkificate.normalize_urls("https://firma.com/detay")  # "firma nokta com bölü detay"
turkificate.normalize_phones("0532 123 45 67")
turkificate.normalize_turkish_ids("10000000146")
turkificate.normalize_companies("Google ve Apple")       # "gugıl ve epıl"
turkificate.normalize_technology_terms("GPT ve API")     # "ci pi ti ve ey pi ay"
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

- The period ordinal form (`3. kat` → "üçüncü kat") is enabled by default. It requires whitespace + a non-whitespace character after the dot, so sentence-final periods are safe. Disable with `period_ordinals=False`.
- The number engine is one-way; the reverse direction (words → digits) is not yet implemented.
- Context-sensitive suffixes (`5'te` → "beşte") are not handled yet.
- Roman numerals and fractions (`3/4`) can be added.

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
