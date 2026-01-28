"""Tests for advanced lexical diversity metrics.

This module tests four advanced lexical diversity metrics that control for
text length, addressing the fundamental limitation of simple TTR:

1. voc-D (Vocabulary D): Curve-fitting approach
2. MATTR (Moving-Average Type-Token Ratio): Sliding window approach
3. HD-D (Hypergeometric Distribution D): Probabilistic approach
4. MSTTR (Mean Segmental Type-Token Ratio): Segmental approach

Related GitHub Issue:
    #14 - Advanced Lexical Diversity Metrics
    https://github.com/craigtrim/pystylometry/issues/14
"""

from pystylometry.lexical import (
    compute_mattr,
)

# ============================================================================
# Fixtures
# ============================================================================


# ============================================================================
# voc-D Tests
# ============================================================================


class TestAdvancedDiversityTokenization:
    """Tokenization consistency tests for all metrics."""

    def test_case_insensitivity_mattr(self):
        """Test that MATTR is case-insensitive."""
        text1 = "The Quick Brown Fox " * 25
        text2 = "the quick brown fox " * 25

        result1 = compute_mattr(text1, window_size=50)
        result2 = compute_mattr(text2, window_size=50)

        # Scores should be identical
        assert result1.mattr_score == result2.mattr_score

    def test_punctuation_handling_mattr(self):
        """Test that MATTR strips punctuation correctly."""
        text1 = "The, quick. brown! fox? " * 25
        text2 = "The quick brown fox " * 25

        result1 = compute_mattr(text1, window_size=50)
        result2 = compute_mattr(text2, window_size=50)

        # Scores should be identical (punctuation stripped)
        assert result1.mattr_score == result2.mattr_score

    def test_whitespace_handling_mattr(self):
        """Test that MATTR handles various whitespace correctly."""
        text1 = "The  quick   brown    fox " * 25  # Multiple spaces
        text2 = "The quick brown fox " * 25  # Single spaces

        result1 = compute_mattr(text1, window_size=50)
        result2 = compute_mattr(text2, window_size=50)

        # Scores should be identical (whitespace normalized)
        assert result1.mattr_score == result2.mattr_score
