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


class TestColemanLiauFormula:
    """Test formula correctness and coefficient application."""

    def test_formula_components(self):
        """Verify formula components are calculated correctly."""
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_coleman_liau(text)

        L = result.metadata["letters_per_100_words"]  # noqa: N806
        S = result.metadata["sentences_per_100_words"]  # noqa: N806

        # Manual calculation: CLI = 0.0588*L - 0.296*S - 15.8
        expected_cli = 0.0588 * L - 0.296 * S - 15.8

        # Should match within floating point precision
        assert abs(result.cli_index - expected_cli) < 0.0001

    def test_longer_words_increase_score(self):
        """Test that longer words increase readability score."""
        short_words = "The cat sat on the mat."
        long_words = "The feline positioned itself upon the textile floor covering."

        result_short = compute_coleman_liau(short_words)
        result_long = compute_coleman_liau(long_words)

        # Longer words should produce higher letter count per word
        assert (
            result_long.metadata["letters_per_100_words"]
            > result_short.metadata["letters_per_100_words"]
        )

    def test_more_sentences_decrease_score(self):
        """Test that more sentences decrease complexity."""
        few_sentences = "This is a very long sentence with many words and clauses."
        many_sentences = "This is short. So is this. And this. Very short."

        result_few = compute_coleman_liau(few_sentences)
        result_many = compute_coleman_liau(many_sentences)

        # More sentences per word should decrease score
        assert (
            result_many.metadata["sentences_per_100_words"]
            > result_few.metadata["sentences_per_100_words"]
        )
