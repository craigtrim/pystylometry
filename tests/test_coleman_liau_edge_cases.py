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

import math

from pystylometry.readability import compute_coleman_liau


class TestColemanLiauEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_string(self):
        """Test empty string input."""
        result = compute_coleman_liau("")

        assert math.isnan(result.cli_index)
        assert math.isnan(result.grade_level)
        assert result.metadata["sentence_count"] == 0
        assert result.metadata["word_count"] == 0
        assert result.metadata["letter_count"] == 0
        assert result.metadata["letters_per_100_words"] == 0.0
        assert result.metadata["sentences_per_100_words"] == 0.0
        assert not result.metadata["reliable"]

    def test_whitespace_only(self):
        """Test string with only whitespace."""
        result = compute_coleman_liau("   \n\t  ")

        assert math.isnan(result.cli_index)
        assert math.isnan(result.grade_level)
        assert not result.metadata["reliable"]

    def test_no_letters(self):
        """Test string with no alphabetic characters."""
        result = compute_coleman_liau("123 456... !!!")

        assert result.metadata["letter_count"] == 0

    def test_very_simple_text(self):
        """Test extremely simple text that might produce negative CLI."""
        text = "Go. Run. Stop. Hi."
        result = compute_coleman_liau(text)

        # Should be clamped at 0
        assert result.grade_level == 0
        # CLI itself might be negative
        assert result.cli_index < 5.0

    def test_single_word(self):
        """Test single word."""
        result = compute_coleman_liau("Hello")

        assert result.metadata["word_count"] == 1
        # Sentence splitter may count this as 1 sentence despite no terminator
        assert result.metadata["sentence_count"] >= 0
        assert not result.metadata["reliable"]
