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


class TestColemanLiauMetadata:
    """Test metadata structure and consistency."""

    def test_metadata_keys_consistent(self):
        """Verify all metadata keys are present regardless of input."""
        test_cases = [
            "",  # Empty
            "Hello",  # Single word
            "The cat sat on the mat.",  # Simple sentence
            " ".join(["word"] * 200) + ".",  # Long text
        ]

        expected_keys = {
            "sentence_count",
            "word_count",
            "letter_count",
            "letters_per_100_words",
            "sentences_per_100_words",
            "reliable",
        }

        for text in test_cases:
            result = compute_coleman_liau(text)
            # Use subset check - implementation may include additional prefixed keys
            assert expected_keys.issubset(set(result.metadata.keys()))

    def test_metadata_values_sensible(self):
        """Test that metadata values are within sensible ranges."""
        text = "The quick brown fox jumps over the lazy dog. The end."
        result = compute_coleman_liau(text)

        # Counts should be non-negative
        assert result.metadata["sentence_count"] >= 0
        assert result.metadata["word_count"] >= 0
        assert result.metadata["letter_count"] >= 0

        # Per-100-words values should be non-negative
        assert result.metadata["letters_per_100_words"] >= 0
        assert result.metadata["sentences_per_100_words"] >= 0

        # Reliable should be boolean
        assert isinstance(result.metadata["reliable"], bool)

    def test_letter_count_excludes_non_alpha(self):
        """Verify letter count only includes alphabetic characters.

        CRITICAL: This test validates the token-based letter counting fix from PR #2.
        See: https://github.com/craigtrim/pystylometry/pull/2

        The implementation counts letters from TOKENIZED words, not raw text.
        This ensures measurement consistency with word count (both use same tokens).

        For "Hello123 World!!! Test@example.com":
        - Tokenizer splits into tokens (exact splitting depends on tokenizer)
        - Letter count: sum of alphabetic chars across all tokens
        - Numbers (123), punctuation (!!!), and symbols (@, .) are excluded
        - Expected: Letters from Hello + World + Test + example + com
        """
        text = "Hello123 World!!! Test@example.com"
        result = compute_coleman_liau(text)

        # Should count only alphabetic characters from all tokens
        # HelloWorldTestexamplecom = 25 letters
        expected_letters = len("HelloWorldTestexamplecom")
        assert result.metadata["letter_count"] == expected_letters
