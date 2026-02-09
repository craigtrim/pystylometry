"""Tests for Unicode dash and hyphen normalization.

Tests for GitHub Issue #58:
https://github.com/craigtrim/pystylometry/issues/58

Verifies that Unicode dash/hyphen variants are correctly normalized:
- Em-dashes and long dashes → space (splits joined words)
- Hyphen variants (general punctuation, math, compatibility, script-specific) → ASCII hyphen
- Soft / invisible hyphens → removed entirely
"""

import pytest

from pystylometry.lexical.bnc_frequency import _normalize_dashes
from pystylometry.lexical.word_class_distribution import (
    compute_word_class_distribution,
)


# ---------------------------------------------------------------------------
# Unit tests: _normalize_dashes function
# ---------------------------------------------------------------------------


class TestEmDashSplitting:
    """Em-dashes, long dashes, and horizontal bars should become spaces."""

    def test_em_dash(self):
        assert _normalize_dashes("and\u2014and") == "and and"

    def test_en_dash(self):
        assert _normalize_dashes("well\u2013known") == "well known"

    def test_horizontal_bar(self):
        assert _normalize_dashes("now\u2015some") == "now some"

    def test_double_oblique_hyphen(self):
        assert _normalize_dashes("a\u2e17b") == "a b"

    def test_hyphen_with_diaeresis(self):
        assert _normalize_dashes("a\u2e1ab") == "a b"

    def test_two_em_dash(self):
        assert _normalize_dashes("a\u2e3ab") == "a b"

    def test_three_em_dash(self):
        assert _normalize_dashes("a\u2e3bb") == "a b"

    def test_multiple_em_dashes(self):
        assert _normalize_dashes("a\u2014b\u2014c") == "a b c"

    def test_em_dash_at_boundaries(self):
        assert _normalize_dashes("\u2014hello\u2014") == " hello "


class TestHyphenNormalization:
    """Unicode hyphen variants should become ASCII hyphen-minus."""

    # General punctuation hyphens
    def test_hyphen(self):
        assert _normalize_dashes("re\u2010enter") == "re-enter"

    def test_non_breaking_hyphen(self):
        assert _normalize_dashes("co\u2011operate") == "co-operate"

    def test_figure_dash(self):
        assert _normalize_dashes("re\u2012enter") == "re-enter"

    # Mathematical minus / dash-like operators
    def test_minus_sign(self):
        assert _normalize_dashes("re\u2212enter") == "re-enter"

    def test_heavy_minus_sign(self):
        assert _normalize_dashes("re\u2796enter") == "re-enter"

    # Compatibility / presentation forms
    def test_small_em_dash(self):
        assert _normalize_dashes("re\ufe58enter") == "re-enter"

    def test_small_hyphen_minus(self):
        assert _normalize_dashes("re\ufe63enter") == "re-enter"

    def test_fullwidth_hyphen_minus(self):
        assert _normalize_dashes("re\uff0denter") == "re-enter"

    # Script-specific hyphenation marks
    def test_armenian_hyphen(self):
        assert _normalize_dashes("a\u058ab") == "a-b"

    def test_hebrew_maqaf(self):
        assert _normalize_dashes("a\u05beb") == "a-b"

    def test_canadian_syllabics_hyphen(self):
        assert _normalize_dashes("a\u1400b") == "a-b"

    def test_katakana_hiragana_double_hyphen(self):
        assert _normalize_dashes("a\u30a0b") == "a-b"

    # Passthrough
    def test_ascii_hyphen_passthrough(self):
        """ASCII hyphen-minus should not be altered."""
        assert _normalize_dashes("mother-in-law") == "mother-in-law"


class TestSoftHyphenRemoval:
    """Soft and invisible hyphens should be removed entirely."""

    def test_soft_hyphen_removed(self):
        assert _normalize_dashes("beau\u00adtiful") == "beautiful"

    def test_multiple_soft_hyphens(self):
        assert _normalize_dashes("in\u00adter\u00adest\u00ading") == "interesting"

    def test_mongolian_todo_soft_hyphen(self):
        assert _normalize_dashes("beau\u1806tiful") == "beautiful"

    def test_invisible_separator(self):
        assert _normalize_dashes("beau\u2063tiful") == "beautiful"

    def test_mongolian_fvs_one(self):
        assert _normalize_dashes("beau\u180btiful") == "beautiful"

    def test_mongolian_fvs_two(self):
        assert _normalize_dashes("beau\u180ctiful") == "beautiful"

    def test_mongolian_fvs_three(self):
        assert _normalize_dashes("beau\u180dtiful") == "beautiful"


class TestNoOpCases:
    """Plain ASCII text should pass through unchanged."""

    def test_plain_text(self):
        assert _normalize_dashes("hello world") == "hello world"

    def test_empty_string(self):
        assert _normalize_dashes("") == ""

    def test_ascii_punctuation(self):
        assert _normalize_dashes("don't stop!") == "don't stop!"


# ---------------------------------------------------------------------------
# Integration tests: word_class_distribution pipeline
# ---------------------------------------------------------------------------


class TestDistributionIntegration:
    """Verify normalization is wired into the word-class distribution pipeline."""

    def test_em_dash_splits_into_separate_tokens(self):
        """'and—and' should produce two lexical tokens, not one unicode token."""
        result = compute_word_class_distribution("and\u2014and")
        assert result.total_words == 2
        assert "unicode.unclassified" not in [
            e.label for e in result.classifications
        ]

    def test_unicode_hyphen_classifies_as_hyphenated(self):
        """'re‑enter' with U+2011 should classify as hyphenated.prefixed."""
        result = compute_word_class_distribution("re\u2011enter")
        labels = [e.label for e in result.classifications]
        assert "hyphenated.prefixed" in labels

    def test_soft_hyphen_produces_clean_token(self):
        """'beau­tiful' with soft hyphen should classify as lexical."""
        result = compute_word_class_distribution("beau\u00adtiful")
        assert result.total_words == 1
        labels = [e.label for e in result.classifications]
        assert "lexical" in labels

    def test_two_em_dash_splits_tokens(self):
        """Two-em dash (U+2E3A) should split joined words."""
        result = compute_word_class_distribution("hello\u2e3aworld")
        assert result.total_words == 2
