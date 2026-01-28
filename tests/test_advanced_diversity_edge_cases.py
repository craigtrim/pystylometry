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
    compute_msttr,
)

# ============================================================================
# Fixtures
# ============================================================================


# ============================================================================
# voc-D Tests
# ============================================================================


class TestAdvancedDiversityEdgeCases:
    """Edge case tests for all metrics."""

    def test_all_unique_words_mattr(self):
        """Test MATTR with all unique words (max diversity)."""
        # Create text with 200 unique words
        text = " ".join([f"unique{i}" for i in range(200)])
        result = compute_mattr(text, window_size=50)

        # MATTR should be 1.0 (perfect diversity)
        assert result.mattr_score == 1.0

    def test_all_unique_words_msttr(self):
        """Test MSTTR with all unique words (max diversity)."""
        # Create text with 200 unique words
        text = " ".join([f"unique{i}" for i in range(200)])
        result = compute_msttr(text, segment_size=100)

        # MSTTR should be 1.0 (perfect diversity)
        assert result.msttr_score == 1.0

    def test_single_word_repeated_mattr(self):
        """Test MATTR with single word repeated (min diversity)."""
        text = "word " * 100
        result = compute_mattr(text, window_size=50)

        # MATTR should be very low (1/50 = 0.02)
        assert result.mattr_score < 0.03

    def test_single_word_repeated_msttr(self):
        """Test MSTTR with single word repeated (min diversity)."""
        text = "word " * 200
        result = compute_msttr(text, segment_size=100)

        # MSTTR should be very low (1/100 = 0.01)
        assert result.msttr_score < 0.02
