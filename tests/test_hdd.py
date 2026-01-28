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

import math

import pytest

from pystylometry.lexical import (
    compute_hdd,
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


class TestHDD:
    """Tests for HD-D (Hypergeometric Distribution D) metric."""

    def test_hdd_basic_functionality(self, simple_text):
        """Test basic HD-D computation with valid text."""
        result = compute_hdd(simple_text)

        # Check all required fields exist
        assert hasattr(result, "hdd_score")
        assert hasattr(result, "sample_size")
        assert hasattr(result, "type_count")
        assert hasattr(result, "token_count")
        assert hasattr(result, "metadata")

        # Check types
        assert isinstance(result.hdd_score, float)
        assert isinstance(result.sample_size, int)
        assert isinstance(result.type_count, int)
        assert isinstance(result.token_count, int)
        assert isinstance(result.metadata, dict)

    def test_hdd_score_range(self, simple_text):
        """Test that HD-D score is between 0 and type_count."""
        result = compute_hdd(simple_text)
        assert 0.0 <= result.hdd_score <= result.type_count

    def test_hdd_score_non_negative(self, simple_text):
        """Test that HD-D score is non-negative."""
        result = compute_hdd(simple_text)
        assert result.hdd_score >= 0.0

    def test_hdd_high_diversity(self, high_diversity_text):
        """Test HD-D with high diversity text produces high score."""
        result = compute_hdd(high_diversity_text, sample_size=42)
        # High diversity text should have high HD-D
        # (many types expected to be unseen in sample)
        assert result.hdd_score > 20

    def test_hdd_low_diversity(self, low_diversity_text):
        """Test HD-D with low diversity text produces low score."""
        result = compute_hdd(low_diversity_text, sample_size=42)
        # Low diversity text should have low HD-D
        # (most types will appear in sample)
        assert result.hdd_score < 5

    def test_hdd_text_too_short(self):
        """Test error handling when text has insufficient tokens."""
        short = "the cat sat"  # 3 tokens
        with pytest.raises(ValueError, match="minimum.*required"):
            compute_hdd(short, sample_size=42)

    def test_hdd_different_sample_sizes(self, simple_text):
        """Test HD-D with different sample sizes."""
        result1 = compute_hdd(simple_text, sample_size=30)
        result2 = compute_hdd(simple_text, sample_size=42)
        result3 = compute_hdd(simple_text, sample_size=60)

        # All should produce valid results
        assert result1.hdd_score >= 0.0
        assert result2.hdd_score >= 0.0
        assert result3.hdd_score >= 0.0

        # HD-D should generally decrease as sample size increases
        # (larger samples more likely to encounter rare types)
        # But this isn't guaranteed, so we just check validity

    def test_hdd_metadata_completeness(self, simple_text):
        """Test that metadata contains all required fields."""
        result = compute_hdd(simple_text)

        assert "total_token_count" in result.metadata
        assert "total_type_count" in result.metadata
        assert "simple_ttr" in result.metadata

    def test_hdd_empty_text(self):
        """Test HD-D with empty text raises error."""
        with pytest.raises(ValueError):
            compute_hdd("")

    def test_hdd_numerical_stability(self, simple_text):
        """Test HD-D doesn't produce NaN or inf."""
        result = compute_hdd(simple_text)
        assert not math.isnan(result.hdd_score)
        assert not math.isinf(result.hdd_score)
