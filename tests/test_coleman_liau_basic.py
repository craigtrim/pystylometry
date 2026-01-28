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


class TestColemanLiauBasic:
    """Test basic Coleman-Liau functionality."""

    def test_simple_sentence(self):
        """Test single simple sentence."""
        text = "The cat sat on the mat."
        result = compute_coleman_liau(text)

        assert isinstance(result.cli_index, float)
        assert isinstance(result.grade_level, (int, float))  # Float for chunked mean
        assert result.grade_level >= 0
        # NOTE: No upper bound check (removed per PR #2 review)
        # Previously checked <= 20, but upper bound was arbitrary
        assert not result.metadata["reliable"]  # < 100 words

    def test_expected_values(self):
        """Test known expected values for calibration.

        NOTE: Expected values changed after PR #2 fix for letter counting.
        See: https://github.com/craigtrim/pystylometry/pull/2

        OLD (buggy): CLI ~1.8, grade 2
        - Counted letters from raw text: "Thequickbrownfoxjumpsoverthelazydog" = 35 letters
        - But counted words from tokens: 9 tokens
        - Incorrect ratio due to measurement inconsistency

        NEW (fixed): CLI ~3.8, grade 4
        - Counts both letters and words from same tokens
        - "The" "quick" "brown" etc. = 9 tokens, 35 letters total
        - Mathematically consistent measurement

        The docstring example will be updated to reflect the corrected values.
        """
        # From docstring example
        text = "The quick brown fox jumps over the lazy dog."
        result = compute_coleman_liau(text)

        # Updated expected values after letter counting fix (PR #2)
        assert abs(result.cli_index - 3.8) < 0.1  # Allow small tolerance
        assert result.grade_level == 4
        assert not result.metadata["reliable"]

    def test_reliable_text(self):
        """Test text that meets reliability threshold."""
        # Generate text with exactly 100 words
        words = ["The", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog"]
        text = " ".join(words * 12)  # 108 words
        text += "."

        result = compute_coleman_liau(text)
        assert result.metadata["reliable"]
        assert result.metadata["word_count"] >= 100
