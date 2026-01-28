"""Comprehensive tests for Coleman-Liau Index computation.

This test suite validates the implementation of the Coleman-Liau Index (CLI)
readability metric as defined in:
    Coleman, M., & Liau, T. L. (1975). A computer readability formula
    designed for machine scoring. Journal of Applied Psychology, 60(2), 283.

CRITICAL IMPLEMENTATION CHANGES (PR #2 Review):
    https://github.com/craigtrim/pystylometry/pull/2

    1. Letter Counting (CORRECTNESS BUG FIX):
       - OLD (buggy): Counted letters from raw text, words from tokenized text
       - NEW (fixed): Count letters from tokenized words only
       - Rationale: Ensures measurement consistency. The Coleman-Liau formula
         requires L (letters per 100 words) to use the same text units for both
         numerator and denominator. Edge cases like emails, URLs, and hyphenated
         words would cause divergence between raw letter count and token count.

    2. Grade Level Bounds (DESIGN CHANGE):
       - OLD: Clamped to [0, 20] range
       - NEW: Lower bound only (0), no upper bound
       - Rationale: Original paper did not specify upper bound. Clamping at 20
         discarded information and made complex texts (PhD dissertations, legal
         documents) indistinguishable. The empirical formula should determine range.
"""

from pystylometry.readability import compute_coleman_liau


class TestColemanLiauUnicode:
    """Test Unicode character handling."""

    def test_unicode_letters(self):
        """Test that Unicode letters are counted."""
        text = "Café résumé naïve façade."
        result = compute_coleman_liau(text)

        # All accented characters should count as letters
        assert result.metadata["letter_count"] > 0

    def test_non_latin_scripts(self):
        """Test handling of non-Latin scripts."""
        # Greek
        text_greek = "Γεια σου κόσμε"
        result = compute_coleman_liau(text_greek)
        assert result.metadata["letter_count"] > 0

        # Cyrillic
        text_cyrillic = "Привет мир"
        result = compute_coleman_liau(text_cyrillic)
        assert result.metadata["letter_count"] > 0

    def test_emoji_excluded(self):
        """Test that emoji are not counted as letters."""
        text = "Hello 😊 World 🌍"
        result = compute_coleman_liau(text)

        # Should only count: HelloWorld
        expected = len("HelloWorld")
        assert result.metadata["letter_count"] == expected
