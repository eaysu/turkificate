"""Lexical data: month names, abbreviations, units, symbols, currencies.

Keeping this data in one place lets the normalizers build their regexes from it
and makes extending the library (adding a new abbreviation, etc.) a one-line change.

The values are intentionally Turkish — they are the spoken/written forms the
library emits.
"""

# 1..12 -> month name
MONTHS = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
    5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
    9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık",
}

# Lexical abbreviations (matched case-insensitively). Keys are lowercase.
ABBREVIATIONS = {
    "dr.": "doktor",
    "prof.": "profesör",
    "doç.": "doçent",
    "yrd.": "yardımcı",
    "av.": "avukat",
    "sn.": "sayın",
    "vs.": "vesaire",
    "vb.": "ve benzeri",
    "vd.": "ve diğerleri",
    "bkz.": "bakınız",
    "örn.": "örneğin",
    "yy.": "yüzyıl",
    "no.": "numara",
    "tel.": "telefon",
    "cad.": "cadde",
    "sok.": "sokak",
    "apt.": "apartman",
    "mah.": "mahalle",
}

# Units of measure (expanded only when they follow a number).
# Longer keys must appear before shorter prefix-matches (e.g. "°C" before "°").
UNITS = {
    "°C": "derece",
    "°F": "fahrenheit",
    "km²": "kilometre kare",
    "m²": "metre kare",
    "m³": "metre küp",
    "km/h": "kilometre bölü saat",
    "km/sa": "kilometre bölü saat",
    "m/s": "metre bölü saniye",
    "kWh": "kilowatt saat",
    "GHz": "gigahertz",
    "MHz": "megahertz",
    "kHz": "kilohertz",
    "Hz": "hertz",
    "kW": "kilowatt",
    "MW": "megawatt",
    "km": "kilometre",
    "cm": "santimetre",
    "mm": "milimetre",
    "kg": "kilogram",
    "mg": "miligram",
    "gr": "gram",
    "ml": "mililitre",
    "lt": "litre",
    "kb": "kilobayt",
    "mb": "megabayt",
    "gb": "gigabayt",
    "tb": "terabayt",
    "sa": "saat",
    "dk": "dakika",
    "sn": "saniye",
    "m": "metre",
    "g": "gram",
    "l": "litre",
}

# Currency symbols and codes -> spoken form.
CURRENCY = {
    "₺": "lira",
    "tl": "lira",
    "try": "lira",
    "$": "dolar",
    "usd": "dolar",
    "€": "avro",
    "eur": "avro",
    "£": "sterlin",
    "gbp": "sterlin",
    "₽": "ruble",
}

# Single-character symbols -> spoken form.
SYMBOLS = {
    "&": "ve",
    "@": "et",
    "°": "derece",
    "×": "çarpı",
    "÷": "bölü",
    "+": "artı",
    "=": "eşittir",
    "₊": "artı",
    "≠": "eşit değil",
    "≤": "küçük eşit",
    "≥": "büyük eşit",
    "√": "karekök",
    "∞": "sonsuz",
    "π": "pi",
}
