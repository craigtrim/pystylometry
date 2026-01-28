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

import pytest

from pystylometry.lexical import (
    compute_hdd,
    compute_mattr,
    compute_msttr,
    compute_vocd_d,
)

# ============================================================================
# Fixtures
# ============================================================================


# ============================================================================
# voc-D Tests
# ============================================================================


@pytest.fixture
def academic_text():
    """Academic-style text sample (400+ tokens)."""
    base = (
        "Research demonstrates that lexical diversity metrics provide "
        "valuable insights into vocabulary richness. However, traditional "
        "type-token ratio exhibits a fundamental limitation: its dependence "
        "on text length. Advanced metrics such as voc-D, MATTR, HD-D, and "
        "MSTTR address this limitation through various mathematical approaches. "
        "These metrics enable more reliable cross-text comparisons regardless "
        "of document length. Consequently, researchers can analyze vocabulary "
        "patterns with greater confidence and precision. "
    )
    return base * 5


@pytest.fixture
def fiction_text():
    """Fiction narrative sample (300+ tokens)."""
    base = (
        "She walked through the ancient forest, marveling at the towering trees. "
        "Sunlight filtered through emerald leaves, casting dancing shadows on "
        "the mossy ground. A gentle breeze whispered secrets among the branches, "
        "while distant birdsong created a melodious symphony. She paused, "
        "listening intently to nature's harmonious composition. "
    )
    return base * 6


@pytest.fixture
def technical_text():
    """Technical documentation sample (300+ tokens)."""
    base = (
        "The function accepts a string parameter and returns a float value. "
        "It tokenizes the input by splitting on whitespace and stripping "
        "punctuation characters. The algorithm then calculates the ratio "
        "of unique tokens to total tokens. This metric provides a quantitative "
        "measure of lexical diversity within the text. "
    )
    return base * 6


class TestAdvancedDiversityRealWorld:
    """Tests with realistic text samples."""

    def test_academic_text_all_metrics(self, academic_text):
        """Test all metrics with academic prose."""
        vocd = compute_vocd_d(academic_text, random_seed=42, min_tokens=100)
        mattr = compute_mattr(academic_text, window_size=50)
        hdd = compute_hdd(academic_text, sample_size=42)
        msttr = compute_msttr(academic_text, segment_size=100)

        # All should produce valid scores
        assert vocd.d_parameter > 0
        assert 0.0 <= mattr.mattr_score <= 1.0
        assert hdd.hdd_score >= 0.0
        assert 0.0 <= msttr.msttr_score <= 1.0

    def test_fiction_text_all_metrics(self, fiction_text):
        """Test all metrics with fiction narrative."""
        vocd = compute_vocd_d(fiction_text, random_seed=42, min_tokens=100)
        mattr = compute_mattr(fiction_text, window_size=50)
        hdd = compute_hdd(fiction_text, sample_size=42)
        msttr = compute_msttr(fiction_text, segment_size=100)

        # All should produce valid scores
        assert vocd.d_parameter > 0
        assert 0.0 <= mattr.mattr_score <= 1.0
        assert hdd.hdd_score >= 0.0
        assert 0.0 <= msttr.msttr_score <= 1.0

    def test_technical_text_all_metrics(self, technical_text):
        """Test all metrics with technical documentation."""
        vocd = compute_vocd_d(technical_text, random_seed=42, min_tokens=100)
        mattr = compute_mattr(technical_text, window_size=50)
        hdd = compute_hdd(technical_text, sample_size=42)
        msttr = compute_msttr(technical_text, segment_size=100)

        # All should produce valid scores
        assert vocd.d_parameter > 0
        assert 0.0 <= mattr.mattr_score <= 1.0
        assert hdd.hdd_score >= 0.0
        assert 0.0 <= msttr.msttr_score <= 1.0
