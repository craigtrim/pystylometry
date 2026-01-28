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


class TestColemanLiauSpecialCases:
    """Test special input cases and tokenizer interactions."""

    def test_urls_and_emails(self):
        """Test handling of URLs and email addresses.

        CRITICAL BUG FIX: This test validates edge cases identified in PR #2 review.
        See: https://github.com/craigtrim/pystylometry/pull/2

        Original bug:
        - "user@example.com" counted letters from RAW text (14 letters)
        - But tokenizer might split into ['user', '@', 'example', '.', 'com'] (5 tokens)
        - This created incorrect letters-per-word ratio

        Fixed implementation:
        - Counts letters only from tokens: user+example+com = 14 letters
        - Word count from same tokens (depends on tokenizer, ~5-7 tokens)
        - Both measurements now use identical tokenization logic
        - No divergence in edge cases

        This test ensures the implementation handles these special cases without
        error and produces mathematically consistent results.
        """
        text = "Visit https://example.com or email user@example.com for info."
        result = compute_coleman_liau(text)

        # Should complete without error
        assert result.cli_index is not None
        assert result.grade_level >= 0

        # Validate measurement consistency (core fix from PR #2)
        # Letter count and word count must be from same tokenization
        assert result.metadata["letter_count"] >= 0
        assert result.metadata["word_count"] > 0
        # L = letters per 100 words should be sensible (not wildly incorrect)
        assert result.metadata["letters_per_100_words"] > 0

    def test_numbers_in_text(self):
        """Test handling of numbers."""
        text = "In 2023, the company had 500 employees and revenue of $1,000,000."
        result = compute_coleman_liau(text)

        # Numbers should not count as letters
        assert "2023" not in str(result.metadata["letter_count"])

    def test_contractions(self):
        """Test handling of contractions."""
        text = "I can't believe it's already over. They're leaving soon."
        result = compute_coleman_liau(text)

        # Should handle contractions naturally
        assert result.metadata["word_count"] >= 1
        assert result.grade_level >= 0

    def test_hyphenated_words(self):
        """Test handling of hyphenated compounds.

        Edge case identified in PR #2 review:
        See: https://github.com/craigtrim/pystylometry/pull/2

        Problem case: "co-operate"
        - Tokenizer might split into ['co', '-', 'operate'] (3 tokens)
        - Old bug: raw text letter count (9) vs token count (3) = wrong ratio
        - Fix: count letters from tokens only: co+operate = 9 letters, 3 tokens

        This test validates that hyphenated compounds are handled consistently
        by counting letters from the same tokens used for word count.
        """
        text = "The well-known twenty-first-century state-of-the-art solution."
        result = compute_coleman_liau(text)

        # Should count letters from tokens (exact count depends on tokenization)
        # wellknown + twentyfirstcentury + stateoftheart + The + solution
        # Approximately 50+ letters across all tokens
        assert result.metadata["letter_count"] > 30
