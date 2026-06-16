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

    def test_urls(self):
        assert turkificate.normalize_urls("https://firma.com/detay") == (
            "firma nokta com bölü detay"
        )

    def test_ordinals_apostrophe(self):
        assert turkificate.normalize_ordinals("5'inci") == "beşinci"

    def test_phones(self):
        expected = "sıfır beş yüz otuz iki yüz yirmi üç kırk beş altmış yedi"
        assert turkificate.normalize_phones("0532 123 45 67") == expected
        assert turkificate.normalize_phones("+90 (532) 123-45-67") == expected
        assert turkificate.normalize_phones("0090 532 123 45 67") == expected
        assert turkificate.normalize_phones("0212 555 12 34") == (
            "sıfır iki yüz on iki beş yüz elli beş on iki otuz dört"
        )

    def test_invalid_phone_untouched(self):
        assert turkificate.normalize_phones("1234567890") == "1234567890"

    def test_turkish_ids(self):
        assert turkificate.normalize_turkish_ids("10000000146") == (
            "bir sıfır sıfır sıfır sıfır sıfır sıfır sıfır bir dört altı"
        )
        assert turkificate.normalize_turkish_ids("100 000 001 46") == (
            "bir sıfır sıfır sıfır sıfır sıfır sıfır sıfır bir dört altı"
        )

    def test_invalid_turkish_id_untouched(self):
        assert turkificate.normalize_turkish_ids("12345678901") == "12345678901"

    def test_companies(self):
        assert turkificate.normalize_companies("Turkcell ve Vodafone") == (
            "türksel ve vodafon"
        )
        assert turkificate.normalize_companies("Garanti BBVA") == (
            "Garanti bebevea"
        )
        assert turkificate.normalize_companies("Google, Apple ve Microsoft") == (
            "gugıl, epıl ve maykrosoft"
        )
        assert turkificate.normalize_companies("YouTube, Spotify ve Netflix") == (
            "yu tub, spotifay ve netfliks"
        )
        assert turkificate.normalize_companies("Burger King, Media Markt ve HP") == (
            "börgır king, medya markt ve eyç pi"
        )

    def test_companies_are_case_insensitive(self):
        assert turkificate.normalize_companies("TURKCELL, vodafone") == (
            "türksel, vodafon"
        )
        assert turkificate.normalize_companies("OPENAI ve github") == (
            "opın ey ay ve git hab"
        )

    def test_technology_terms(self):
        assert turkificate.normalize_technology_terms("AI, LLM, API ve GraphQL") == (
            "ey ay, el el em, ey pi ay ve graf kyu el"
        )
        assert turkificate.normalize_technology_terms("FP16, T5 ve K8s") == (
            "ef pi on altı, ti fayv ve key eyt es"
        )

    def test_technology_terms_do_not_match_inside_words(self):
        assert turkificate.normalize_technology_terms("PLAIN") == "PLAIN"


class TestPipeline:
    def test_feature_selection_isolation(self):
        tn = TurkishNormalizer(features=["times"])
        out = tn.normalize("14:30 ve %50")
        assert "on dört otuz" in out
        assert "%50" in out          # percent not selected -> untouched

    def test_companies_can_be_selected_or_left_out(self):
        assert TurkishNormalizer(features=["companies"]).normalize("Turkcell 100 TL") == (
            "türksel 100 TL"
        )
        assert TurkishNormalizer(features=["currency"]).normalize("Turkcell 100 TL") == (
            "Turkcell yüz lira"
        )

    def test_technology_terms_can_be_selected_or_left_out(self):
        assert TurkishNormalizer(features=["technology_terms"]).normalize("GPT ve 2") == (
            "ci pi ti ve 2"
        )
        assert TurkishNormalizer(features=["numbers"]).normalize("GPT ve 2") == (
            "GPT ve iki"
        )

    def test_all_keyword(self):
        assert TurkishNormalizer(features="all").normalize("%50") == "yüzde elli"
        assert TurkishNormalizer(features=["all"]).normalize("%50") == "yüzde elli"
        assert TurkishNormalizer(features=turkificate.ALL).normalize("%50") == "yüzde elli"

    def test_full_pipeline(self):
        out = turkificate.normalize("Dr. Ali 01.01.2024'te 100 TL ödedi.")
        assert out == "doktor Ali bir Ocak iki bin yirmi dört'te yüz lira ödedi."

    def test_full_pipeline_handles_phones_and_turkish_ids_before_numbers(self):
        out = turkificate.normalize("Tel: 0532 123 45 67, TC: 10000000146")
        assert out == (
            "Tel: sıfır beş yüz otuz iki yüz yirmi üç kırk beş altmış yedi, "
            "TC: bir sıfır sıfır sıfır sıfır sıfır sıfır sıfır bir dört altı"
        )

    def test_full_pipeline_handles_companies(self):
        out = turkificate.normalize("Turkcell, Vodafone ve Garanti BBVA")
        assert out == "türksel, vodafon ve Garanti bebevea"

    def test_full_pipeline_handles_technology_terms_before_numbers(self):
        out = turkificate.normalize("GPT, FP16 ve K8s 2024")
        assert out == "ci pi ti, ef pi on altı ve key eyt es iki bin yirmi dört"

    def test_main_function_and_alias(self):
        text = "3 elma"
        assert turkificate.turkificate(text) == "üç elma"
        assert turkificate.turkificate(text) == turkificate.normalize(text)

    def test_unknown_feature_raises(self):
        with pytest.raises(ValueError):
            TurkishNormalizer(features=["no_such_concept"])
