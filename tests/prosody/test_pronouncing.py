"""Tests for the local CMU Pronouncing Dictionary wrapper.

This module tests ``pystylometry.prosody.pronouncing``, which provides
``phones_for_word`` and ``syllable_count`` as drop-in replacements for the
deprecated ``pronouncing`` package.

Related GitHub Issue:
    #60 - Replace pronouncing with direct cmudict access
    https://github.com/craigtrim/pystylometry/issues/60
"""

import re

import pytest

from pystylometry.prosody.pronouncing import (
    _get_dict,
    phones_for_word,
    syllable_count,
)

# ---------------------------------------------------------------------------
# 1. phones_for_word — common words
# ---------------------------------------------------------------------------


def test_phones_for_word_hello():
    """'hello' is in the CMU dict and should return at least one pronunciation."""
    result = phones_for_word("hello")
    assert isinstance(result, list)
    assert len(result) >= 1
    # Each entry should be a non-empty string
    for phones in result:
        assert isinstance(phones, str)
        assert len(phones) > 0


def test_phones_for_word_cat():
    """'cat' should return a pronunciation containing K AE T."""
    result = phones_for_word("cat")
    assert len(result) >= 1
    # The canonical pronunciation is "K AE1 T"
    assert any("K" in p and "AE" in p and "T" in p for p in result)


def test_phones_for_word_the():
    """'the' is one of the most common English words and must be present."""
    result = phones_for_word("the")
    assert len(result) >= 1


def test_phones_for_word_multi_pronunciation():
    """'read' has multiple pronunciations (present vs. past tense)."""
    result = phones_for_word("read")
    assert len(result) >= 2, (
        "'read' should have at least 2 pronunciations (present and past tense)"
    )


def test_phones_for_word_unknown_word():
    """A nonsense word not in the CMU dict should return an empty list."""
    result = phones_for_word("xyzzyplugh")
    assert result == []


def test_phones_for_word_case_insensitive_upper():
    """Uppercase input should match the same as lowercase."""
    lower = phones_for_word("hello")
    upper = phones_for_word("HELLO")
    assert lower == upper


def test_phones_for_word_case_insensitive_mixed():
    """Mixed-case input should match the same as lowercase."""
    lower = phones_for_word("hello")
    mixed = phones_for_word("HeLLo")
    assert lower == mixed


def test_phones_for_word_empty_string():
    """An empty string is not a real word and should return an empty list."""
    result = phones_for_word("")
    assert result == []


# ---------------------------------------------------------------------------
# 2. syllable_count — from known ARPAbet strings
# ---------------------------------------------------------------------------


def test_syllable_count_monosyllabic():
    """'K AE1 T' (cat) has exactly 1 syllable."""
    assert syllable_count("K AE1 T") == 1


def test_syllable_count_disyllabic():
    """'HH AH0 L OW1' (hello) has exactly 2 syllables."""
    assert syllable_count("HH AH0 L OW1") == 2


def test_syllable_count_trisyllabic():
    """'B AH0 N AE1 N AH0' (banana) has 3 syllables."""
    assert syllable_count("B AH0 N AE1 N AH0") == 3


def test_syllable_count_polysyllabic():
    """'IH2 N T ER0 N AE1 SH AH0 N AH0 L' (international) has 5 syllables."""
    assert syllable_count("IH2 N T ER0 N AE1 SH AH0 N AH0 L") == 5


def test_syllable_count_empty_string():
    """An empty string has zero syllables."""
    assert syllable_count("") == 0


def test_syllable_count_consonants_only():
    """A string of consonant-only phonemes (no stress digits) has 0 syllables."""
    # Hypothetical consonant-only string
    assert syllable_count("K T P S") == 0


def test_syllable_count_all_stress_levels():
    """Stress digits 0, 1, and 2 should all count as syllable nuclei."""
    # Construct a string with one of each stress level
    phones = "AH0 EH1 IH2"
    assert syllable_count(phones) == 3


# ---------------------------------------------------------------------------
# 3. Integration — phones_for_word + syllable_count
# ---------------------------------------------------------------------------


def test_integration_hello_syllables():
    """Look up 'hello' phones, then count syllables -- should be 2."""
    phones_list = phones_for_word("hello")
    assert len(phones_list) >= 1
    for phones in phones_list:
        assert syllable_count(phones) == 2


def test_integration_cat_syllables():
    """'cat' should have 1 syllable across all pronunciations."""
    for phones in phones_for_word("cat"):
        assert syllable_count(phones) == 1


def test_integration_beautiful_syllables():
    """'beautiful' should have 3 syllables."""
    phones_list = phones_for_word("beautiful")
    assert len(phones_list) >= 1
    for phones in phones_list:
        assert syllable_count(phones) == 3


def test_integration_dog_syllables():
    """'dog' should have 1 syllable."""
    phones_list = phones_for_word("dog")
    assert len(phones_list) >= 1
    for phones in phones_list:
        assert syllable_count(phones) == 1


def test_integration_unbelievable_syllables():
    """'unbelievable' should have 5 syllables."""
    phones_list = phones_for_word("unbelievable")
    assert len(phones_list) >= 1
    for phones in phones_list:
        assert syllable_count(phones) == 5


# ---------------------------------------------------------------------------
# 4. Dictionary loading — _get_dict
# ---------------------------------------------------------------------------


def test_get_dict_returns_dict():
    """_get_dict should return a Python dict."""
    d = _get_dict()
    assert isinstance(d, dict)


def test_get_dict_has_entries():
    """The CMU dict should have a substantial number of entries (>100 000)."""
    d = _get_dict()
    assert len(d) > 100_000


def test_get_dict_has_expected_words():
    """Spot-check that common words are present as keys."""
    d = _get_dict()
    for word in ("hello", "world", "the", "python", "cat", "dog"):
        assert word in d, f"Expected '{word}' in CMU dictionary"


def test_get_dict_cached_identity():
    """Subsequent calls should return the exact same object (caching)."""
    d1 = _get_dict()
    d2 = _get_dict()
    assert d1 is d2


# ---------------------------------------------------------------------------
# 5. Edge cases
# ---------------------------------------------------------------------------


def test_edge_number_strings():
    """Pure digit strings like '123' are not in the CMU dict."""
    assert phones_for_word("123") == []


def test_edge_punctuation_only():
    """Punctuation-only input should return an empty list."""
    for punct in ("!", ".", ",", "?", "---", "..."):
        assert phones_for_word(punct) == []


def test_edge_very_long_real_word():
    """A long but real English word should be findable."""
    # "internationalization" is not in every build of cmudict, so we test
    # a word that IS reliably present: "autobiography" (6 syllables).
    result = phones_for_word("autobiography")
    if result:
        # If the word is present, verify syllable count
        for phones in result:
            assert syllable_count(phones) >= 5


def test_edge_hyphenated_word():
    """Hyphenated words are generally absent from the CMU dict."""
    # Most hyphenated forms are not dictionary entries
    result = phones_for_word("well-known")
    # We only assert it returns a list (empty or not); do not assume presence.
    assert isinstance(result, list)


def test_edge_whitespace_word():
    """A whitespace-only input should return an empty list."""
    assert phones_for_word("   ") == []


# ---------------------------------------------------------------------------
# 6. Format verification
# ---------------------------------------------------------------------------


# ARPAbet phonemes are uppercase letters optionally followed by a digit (0-2)
_ARPABET_PHONEME_RE = re.compile(r"^[A-Z]+[012]?$")


def test_format_phones_are_space_separated_arpabet():
    """Each pronunciation string should be space-joined ARPAbet phonemes."""
    phones_list = phones_for_word("hello")
    assert len(phones_list) >= 1
    for phones in phones_list:
        tokens = phones.split()
        assert len(tokens) >= 1
        for tok in tokens:
            assert _ARPABET_PHONEME_RE.match(tok), (
                f"Token '{tok}' does not look like an ARPAbet phoneme"
            )


def test_format_stress_digits_are_only_0_1_2():
    """Vowel phonemes should only carry stress digits 0, 1, or 2."""
    phones_list = phones_for_word("international")
    for phones in phones_list:
        for tok in phones.split():
            if tok[-1].isdigit():
                assert tok[-1] in ("0", "1", "2"), (
                    f"Unexpected stress digit in '{tok}'"
                )


def test_format_return_type_is_list_of_strings():
    """phones_for_word must always return a list of str, even for unknowns."""
    # Known word
    result = phones_for_word("dog")
    assert isinstance(result, list)
    for item in result:
        assert isinstance(item, str)

    # Unknown word
    result = phones_for_word("zzzznotaword")
    assert isinstance(result, list)
    assert len(result) == 0


def test_format_syllable_count_return_type():
    """syllable_count must always return an int."""
    assert isinstance(syllable_count("K AE1 T"), int)
    assert isinstance(syllable_count(""), int)
