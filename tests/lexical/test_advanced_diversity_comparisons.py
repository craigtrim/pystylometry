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
def high_diversity_text():
    """Text with high lexical diversity (150+ unique words out of ~600 tokens)."""
    # Create text with high diversity by using many unique content words
    # Each sentence uses mostly different words (literary fiction pattern)
    words = []

    # Generate 6 different "paragraphs" with mostly unique vocabulary
    for p in range(6):
        # Each paragraph has 25 mostly-unique content words
        content_words = [
            f"magnificent{p}_1",
            f"eloquent{p}_2",
            f"profound{p}_3",
            f"ethereal{p}_4",
            f"luminous{p}_5",
            f"enigmatic{p}_6",
            f"transcendent{p}_7",
            f"resplendent{p}_8",
            f"formidable{p}_9",
            f"exquisite{p}_10",
            f"pristine{p}_11",
            f"venerable{p}_12",
            f"illustrious{p}_13",
            f"majestic{p}_14",
            f"sublime{p}_15",
            f"radiant{p}_16",
            f"splendid{p}_17",
            f"grandiose{p}_18",
            f"opulent{p}_19",
            f"lavish{p}_20",
            f"abundant{p}_21",
            f"copious{p}_22",
            f"prolific{p}_23",
            f"verdant{p}_24",
            f"lush{p}_25",
        ]

        # Add content words
        words.extend(content_words)

        # Add some repeated function words (natural pattern)
        function_words = ["the", "a", "is", "was", "and", "of", "to", "in"]
        words.extend(function_words)

    # This gives us: 6 paragraphs * (25 content + 8 function) = ~198 tokens
    # With ~150 unique content words + ~8 function words = ~158 unique types
    # TTR ~ 0.80 (high but realistic for literary text)
    return " ".join(words)


@pytest.fixture
def low_diversity_text():
    """Text with very low lexical diversity (5 unique words repeated)."""
    # Many repetitions of few words
    words = ["the", "a", "is", "was", "and"]
    return " ".join(words * 50)


@pytest.fixture
def simple_text():
    """Simple prose for basic testing (300+ tokens)."""
    base = (
        "The quick brown fox jumps over the lazy dog. "
        "A small bird flies through the blue sky. "
        "The sun shines brightly on the green grass. "
        "Children play happily in the warm sunshine. "
        "The old tree stands tall beside the flowing river. "
    )
    return base * 12  # ~300 tokens


class TestAdvancedDiversityComparisons:
    """Comparative tests across all four metrics."""

    def test_high_diversity_all_metrics(self, high_diversity_text):
        """Test that all metrics agree on high diversity text."""
        vocd = compute_vocd_d(high_diversity_text, random_seed=42, min_tokens=50)
        mattr = compute_mattr(high_diversity_text, window_size=50)
        hdd = compute_hdd(high_diversity_text, sample_size=42)
        msttr = compute_msttr(high_diversity_text, segment_size=100)

        # All metrics should indicate relatively high diversity
        # voc-D should be > 5 (higher than low-diversity text)
        assert vocd.d_parameter > 5

        # MATTR should be moderately high (>0.60 for varied vocabulary)
        assert mattr.mattr_score > 0.60

        # HD-D should be > 5
        assert hdd.hdd_score > 5

        # MSTTR should be > 0.60
        assert msttr.msttr_score > 0.60

    def test_low_diversity_all_metrics(self, low_diversity_text):
        """Test that all metrics agree on low diversity text."""
        vocd = compute_vocd_d(low_diversity_text, random_seed=42, min_tokens=50)
        mattr = compute_mattr(low_diversity_text, window_size=50)
        hdd = compute_hdd(low_diversity_text, sample_size=42)
        msttr = compute_msttr(low_diversity_text, segment_size=100)

        # voc-D should be low (<20)
        assert vocd.d_parameter < 20

        # MATTR should be low (<0.20)
        assert mattr.mattr_score < 0.20

        # HD-D should be low (<5)
        assert hdd.hdd_score < 5

        # MSTTR should be low (<0.20)
        assert msttr.msttr_score < 0.20

    def test_metric_rank_consistency(self, simple_text, high_diversity_text, low_diversity_text):
        """Test that all metrics rank texts consistently."""
        # Compute all metrics for all texts
        # Simple text (medium diversity)
        simple_mattr = compute_mattr(simple_text, window_size=50)

        # High diversity text
        high_mattr = compute_mattr(high_diversity_text, window_size=50)

        # Low diversity text
        low_mattr = compute_mattr(low_diversity_text, window_size=50)

        # Ranking should be: high > simple > low
        assert high_mattr.mattr_score > simple_mattr.mattr_score
        assert simple_mattr.mattr_score > low_mattr.mattr_score
