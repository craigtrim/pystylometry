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


class TestColemanLiauRounding:
    """Test rounding behavior and boundary values."""

    def test_grade_level_is_numeric(self):
        """Verify grade level is always a number (float for mean across chunks)."""
        texts = [
            "The cat sat on the mat.",
            "A very long and complex sentence with many subordinate clauses.",
            "Go.",
        ]

        for text in texts:
            result = compute_coleman_liau(text)
            assert isinstance(result.grade_level, (int, float))

    def test_lower_bound_clamping(self):
        """Test that negative CLI values are clamped to grade 0."""
        # Very simple text should produce negative CLI
        simple = "Go. Run. Stop. Hi. Yes. No."
        result = compute_coleman_liau(simple)

        assert result.grade_level == 0
        # But CLI itself can be negative
        assert result.cli_index < 0

    def test_no_upper_bound_clamping(self):
        """Test that very high CLI values are NOT clamped (no upper bound).

        IMPORTANT: This test was changed during PR #2 review.
        Previously tested that grade level was clamped to 20, but that upper
        bound was removed as it was arbitrary and not from Coleman & Liau (1975).

        See PR #2 review: https://github.com/craigtrim/pystylometry/pull/2

        Rationale for removal:
        - Original paper calibrated to grades 1-16 but specified no upper bound
        - Clamping discarded information about text complexity
        - PhD dissertations (grade 25+) and legal documents (grade 30+) should
          be distinguishable, not all reported as grade 20

        This test now verifies that extremely complex text CAN exceed grade 20.
        """
        # Create extremely complex text with very long words
        complex_words = [
            "antidisestablishmentarianism",
            "supercalifragilisticexpialidocious",
            "pneumonoultramicroscopicsilicovolcanoconiosis",
        ]
        # One very long sentence to reduce sentence count
        text = " ".join(complex_words * 50) + "."

        result = compute_coleman_liau(text)

        # Should be very high (no upper bound)
        # The empirical formula determines the actual grade level
        assert result.grade_level > 20  # Verify it exceeds the old arbitrary cap
        assert isinstance(result.grade_level, (int, float))  # Numeric (float for chunked mean)
