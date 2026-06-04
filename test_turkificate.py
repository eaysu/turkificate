"""turkificate test suite. Run with: pytest"""

import pytest

import turkificate
from turkificate import TurkishNormalizer
from turkificate.numbers import integer_to_words, integer_to_ordinal, read_number


class TestNumberEngine:
    def test_cardinals(self):
        assert integer_to_words(0) == "sıfır"
        assert integer_to_words(100) == "yüz"
        assert integer_to_words(1000) == "bin"
        assert integer_to_words(2000) == "iki bin"
        assert integer_to_words(1_000_000) == "bir milyon"
        assert integer_to_words(1234567) == (
            "bir milyon iki yüz otuz dört bin beş yüz altmış yedi"
        )
        assert integer_to_words(-5) == "eksi beş"

    def test_ordinals(self):
        assert integer_to_ordinal(1) == "birinci"
        assert integer_to_ordinal(4) == "dördüncü"   # consonant softening
        assert integer_to_ordinal(2) == "ikinci"     # vowel-ending stem
        assert integer_to_ordinal(100) == "yüzüncü"

    def test_decimals(self):
        assert read_number("3,14") == "üç virgül on dört"
        assert read_number("3,05") == "üç virgül sıfır beş"
        assert read_number("1.234,5") == "bin iki yüz otuz dört virgül beş"


class TestNormalizers:
    def test_dates(self):
        assert turkificate.normalize_dates("15.03.2024") == (
            "on beş Mart iki bin yirmi dört"
        )

    def test_invalid_date_untouched(self):
        assert turkificate.normalize_dates("32.03.2024") == "32.03.2024"

    def test_percent_before_number(self):
        assert turkificate.normalize_percent("%50") == "yüzde elli"

    def test_currency(self):
        assert turkificate.normalize_currency("100 TL") == "yüz lira"
        assert turkificate.normalize_currency("$50") == "elli dolar"

    def test_units(self):
        assert turkificate.normalize("42 km") == "kırk iki kilometre"
        # the 'm' inside "milyon" must not be mistaken for the metre unit
        assert turkificate.normalize("3 milyon") == "üç milyon"

    def test_abbreviations(self):
        assert turkificate.normalize_abbreviations("Dr. Ahmet") == "doktor Ahmet"

    def test_ordinals_apostrophe(self):
        assert turkificate.normalize_ordinals("5'inci") == "beşinci"


class TestPipeline:
    def test_feature_selection_isolation(self):
        tn = TurkishNormalizer(features=["times"])
        out = tn.normalize("14:30 ve %50")
        assert "on dört otuz" in out
        assert "%50" in out          # percent not selected -> untouched

    def test_all_keyword(self):
        assert TurkishNormalizer(features="all").normalize("%50") == "yüzde elli"
        assert TurkishNormalizer(features=["all"]).normalize("%50") == "yüzde elli"
        assert TurkishNormalizer(features=turkificate.ALL).normalize("%50") == "yüzde elli"

    def test_full_pipeline(self):
        out = turkificate.normalize("Dr. Ali 01.01.2024'te 100 TL ödedi.")
        assert out == "doktor Ali bir Ocak iki bin yirmi dört'te yüz lira ödedi."

    def test_main_function_and_alias(self):
        text = "3 elma"
        assert turkificate.turkificate(text) == "üç elma"
        assert turkificate.turkificate(text) == turkificate.normalize(text)

    def test_unknown_feature_raises(self):
        with pytest.raises(ValueError):
            TurkishNormalizer(features=["no_such_concept"])
