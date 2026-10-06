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

    def test_calendar_invalid_dates_are_untouched_in_full_pipeline(self):
        assert turkificate.normalize("31.04.2026") == "31.04.2026"
        assert turkificate.normalize("29.02.2025") == "29.02.2025"
        assert turkificate.normalize("2025-02-29") == "2025-02-29"
        assert turkificate.normalize("29.02.2024") == "yirmi dokuz Şubat iki bin yirmi dört"

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
            "eay, el el em, ey pi ay ve graf kyu el"
        )
        assert turkificate.normalize_technology_terms("AGI") == "ey ci ay"
        assert turkificate.normalize_technology_terms("FP16, T5 ve K8s") == (
            "ef pi on altı, ti fayv ve key eyt es"
        )
        assert turkificate.normalize_technology_terms("5G") == "beş ge"
        assert turkificate.normalize_technology_terms("Docker") == "dokır"

    def test_technology_terms_do_not_match_inside_words(self):
        assert turkificate.normalize_technology_terms("PLAIN") == "PLAIN"

    def test_custom_lexicon_overrides_bundled_pronunciations(self):
        normalizer = TurkishNormalizer(lexicon={"OpenAI": "open ey ay", "Acme Labs": "ekmi lebs"})
        assert normalizer.normalize("OpenAI ve Acme Labs") == "open ey ay ve ekmi lebs"
        assert turkificate.normalize_with_lexicon("OpenAI", {"OpenAI": "open ey ay"}) == "open ey ay"

    def test_custom_lexicon_is_selected_with_explicit_features(self):
        normalizer = TurkishNormalizer(features=["numbers"], lexicon={"kod": "şifre"})
        assert normalizer.normalize("kod 2") == "şifre iki"
        with pytest.raises(TypeError):
            TurkishNormalizer(lexicon=[("kod", "şifre")])


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
        assert out == "doktor Ali bir Ocak iki bin yirmi dörtte yüz lira ödedi."

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

    def test_full_pipeline_handles_5g_before_units(self):
        assert turkificate.normalize("Turkcell 5G") == "türksel beş ge"

    def test_main_function_and_alias(self):
        text = "3 elma"
        assert turkificate.turkificate(text) == "üç elma"
        assert turkificate.turkificate(text) == turkificate.normalize(text)

    def test_unknown_feature_raises(self):
        with pytest.raises(ValueError):
            TurkishNormalizer(features=["no_such_concept"])


class TestAdvancedNormalization:
    def test_productive_suffix_harmony(self):
        assert turkificate.normalize("5'te") == "beşte"
        assert turkificate.normalize("01.01.2026'da") == "bir Ocak iki bin yirmi altıda"
        assert turkificate.normalize("09:30'da") == "dokuz otuzda"
        assert turkificate.normalize("5 kg'dan") == "beş kilogramdan"
        assert turkificate.normalize("%12,5'lik") == "yüzde on iki virgül beşlik"

    def test_number_suffix_regression_matrix(self):
        normalizer = TurkishNormalizer(features=["numbers"])
        expected = {
            "4'ü": "dördü",
            "4'e": "dörde",
            "4'te": "dörtte",
            "4'ten": "dörtten",
            "4'ün": "dördün",
            "3'ü": "üçü",
            "5'lik": "beşlik",
        }
        for source, spoken in expected.items():
            assert normalizer.normalize(source) == spoken

    def test_currency_minor_units_and_suffixes(self):
        assert turkificate.normalize("5 TL'lik") == "beş liralık"
        assert turkificate.normalize("3,99 TL'ye") == "üç lira doksan dokuz kuruşa"
        assert turkificate.normalize("$1,25") == "bir dolar yirmi beş sent"

    def test_iso_dates_fractions_and_ranges(self):
        assert turkificate.normalize("2026-01-01'de") == "bir Ocak iki bin yirmi altıda"
        assert turkificate.normalize("nüfusun 2/3'ü") == "nüfusun iki bölü üçü"
        assert turkificate.normalize("10-15 yaş") == "on tire on beş yaş"

    def test_contextual_roman_numerals(self):
        assert turkificate.normalize("IV. Murat") == "dördüncü Murat"
        assert turkificate.normalize("XXI. yüzyıl") == "yirmi birinci yüzyıl"
        assert turkificate.normalize("IV vitamin") == "IV vitamin"

    def test_valid_turkish_iban(self):
        iban = "TR330006100519786457841326"
        assert turkificate.normalize_ibans(iban) == (
            "te re üç üç sıfır sıfır sıfır altı bir sıfır sıfır beş bir dokuz yedi "
            "sekiz altı dört beş yedi sekiz dört bir üç iki altı"
        )
        assert turkificate.normalize_ibans("TR330006100519786457841327") == "TR330006100519786457841327"

    def test_detailed_ambiguity_policies(self):
        normalizer = TurkishNormalizer()
        eager = normalizer.normalize_detailed("Sürüm 1.234 hazır.")
        assert eager.text == "Sürüm bin iki yüz otuz dört hazır."
        assert not eager.complete and eager.issues[0].start == 6

        preserved = normalizer.normalize_detailed(
            "Sürüm 1.234 hazır.", ambiguity_policy="preserve"
        )
        assert preserved.text == "Sürüm 1.234 hazır."
        assert not preserved.complete

        with pytest.raises(turkificate.NormalizationAmbiguityError):
            normalizer.normalize_detailed("Sürüm 1.234 hazır.", ambiguity_policy="reject")
        with pytest.raises(ValueError):
            normalizer.normalize_detailed("1", ambiguity_policy="unknown")
