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


class TestColemanLiauReliability:
    """Test reliability flag behavior."""

    def test_reliability_threshold_exact(self):
        """Test reliability at exact threshold.

        NOTE: Token count corrected after understanding tokenizer behavior.
        Punctuation like periods are typically NOT counted as separate tokens
        by word tokenizers - they're stripped or attached to words.

        The reliability threshold is 100 words (tokens), so we test:
        - 99 words → not reliable
        - 100 words → reliable
        """
        # Exactly 99 words (tokenizer counts words, not punctuation)
        text = " ".join(["word"] * 99) + "."
        result = compute_coleman_liau(text)
        assert not result.metadata["reliable"]
        assert result.metadata["word_count"] == 99

        # Exactly 100 words (tokenizer counts words, not punctuation)
        text = " ".join(["word"] * 100) + "."
        result = compute_coleman_liau(text)
        assert result.metadata["reliable"]
        assert result.metadata["word_count"] == 100

    def test_reliability_flag_type(self):
        """Verify reliability is always a boolean."""
        texts = ["", "Short.", " ".join(["word"] * 200)]

        for text in texts:
            result = compute_coleman_liau(text)
            assert isinstance(result.metadata["reliable"], bool)
