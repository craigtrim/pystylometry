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
    compute_mattr,
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


class TestMATTR:
    """Tests for MATTR (Moving-Average Type-Token Ratio) metric."""

    def test_mattr_basic_functionality(self, simple_text):
        """Test basic MATTR computation with valid text."""
        result = compute_mattr(simple_text)

        # Check all required fields exist
        assert hasattr(result, "mattr_score")
        assert hasattr(result, "window_size")
        assert hasattr(result, "window_count")
        assert hasattr(result, "ttr_std_dev")
        assert hasattr(result, "min_ttr")
        assert hasattr(result, "max_ttr")
        assert hasattr(result, "metadata")

        # Check types
        assert isinstance(result.mattr_score, float)
        assert isinstance(result.window_size, int)
        assert isinstance(result.window_count, int)
        assert isinstance(result.ttr_std_dev, float)
        assert isinstance(result.min_ttr, float)
        assert isinstance(result.max_ttr, float)
        assert isinstance(result.metadata, dict)

    def test_mattr_score_range(self, simple_text):
        """Test that MATTR score is between 0 and 1."""
        result = compute_mattr(simple_text)
        assert 0.0 <= result.mattr_score <= 1.0

    def test_mattr_min_max_range(self, simple_text):
        """Test that min_ttr <= mattr_score <= max_ttr (with floating point tolerance)."""
        result = compute_mattr(simple_text)
        # Use epsilon tolerance for floating point comparison
        epsilon = 1e-10
        assert result.min_ttr - epsilon <= result.mattr_score <= result.max_ttr + epsilon

    def test_mattr_window_count(self, simple_text):
        """Test that window_count = token_count - window_size + 1."""
        result = compute_mattr(simple_text, window_size=50)
        token_count = result.metadata["total_token_count"]

        expected_window_count = token_count - 50 + 1
        assert result.window_count == expected_window_count

    def test_mattr_high_diversity(self, high_diversity_text):
        """Test MATTR with high diversity text produces high score."""
        result = compute_mattr(high_diversity_text, window_size=50)
        # High diversity text should have MATTR > 0.60
        assert result.mattr_score > 0.60

    def test_mattr_low_diversity(self, low_diversity_text):
        """Test MATTR with low diversity text produces low score."""
        result = compute_mattr(low_diversity_text, window_size=50)
        # Low diversity text should have MATTR < 0.20
        assert result.mattr_score < 0.20

    def test_mattr_text_too_short(self):
        """Test error handling when text has insufficient tokens."""
        short = "the cat sat"  # 3 tokens
        with pytest.raises(ValueError, match="minimum.*required"):
            compute_mattr(short, window_size=50)

    def test_mattr_exact_window_size(self):
        """Test text exactly equal to window size."""
        text = "the cat sat on the mat and ate food here"  # 10 words
        result = compute_mattr(text, window_size=10)

        # Should have exactly 1 window
        assert result.window_count == 1
        # std_dev should be 0 (only one window)
        assert result.ttr_std_dev == 0.0
        # min == max == mattr_score
        assert result.min_ttr == result.max_ttr == result.mattr_score

    def test_mattr_different_window_sizes(self, simple_text):
        """Test MATTR with different window sizes."""
        result1 = compute_mattr(simple_text, window_size=30)
        result2 = compute_mattr(simple_text, window_size=50)
        result3 = compute_mattr(simple_text, window_size=70)

        # All should produce valid results
        assert 0.0 <= result1.mattr_score <= 1.0
        assert 0.0 <= result2.mattr_score <= 1.0
        assert 0.0 <= result3.mattr_score <= 1.0

    def test_mattr_std_dev_non_negative(self, simple_text):
        """Test that standard deviation is non-negative."""
        result = compute_mattr(simple_text)
        assert result.ttr_std_dev >= 0.0

    def test_mattr_metadata_completeness(self, simple_text):
        """Test that metadata contains all required fields."""
        result = compute_mattr(simple_text)

        assert "total_token_count" in result.metadata
        assert "total_type_count" in result.metadata
        assert "simple_ttr" in result.metadata

    def test_mattr_empty_text(self):
        """Test MATTR with empty text raises error."""
        with pytest.raises(ValueError):
            compute_mattr("")
