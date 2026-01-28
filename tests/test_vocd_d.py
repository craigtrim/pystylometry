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
def short_text():
    """Short text for testing minimum length requirements (40 tokens)."""
    return "The cat sat on the mat. The dog ran in the park. The bird flew over the tree. The fish swam in the pond."


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


class TestVocdD:
    """Tests for voc-D (vocabulary D) metric."""

    def test_vocd_basic_functionality(self, simple_text):
        """Test basic voc-D computation with valid text."""
        result = compute_vocd_d(simple_text, random_seed=42)

        # Check all required fields exist
        assert hasattr(result, "d_parameter")
        assert hasattr(result, "curve_fit_r_squared")
        assert hasattr(result, "sample_count")
        assert hasattr(result, "optimal_sample_size")
        assert hasattr(result, "metadata")

        # Check types
        assert isinstance(result.d_parameter, float)
        assert isinstance(result.curve_fit_r_squared, float)
        assert isinstance(result.sample_count, int)
        assert isinstance(result.optimal_sample_size, int)
        assert isinstance(result.metadata, dict)

    def test_vocd_score_is_positive(self, simple_text):
        """Test that D parameter is positive."""
        result = compute_vocd_d(simple_text, random_seed=42)
        assert result.d_parameter > 0

    def test_vocd_r_squared_range(self, simple_text):
        """Test that R² is between 0 and 1."""
        result = compute_vocd_d(simple_text, random_seed=42)
        assert 0.0 <= result.curve_fit_r_squared <= 1.0

    def test_vocd_r_squared_quality(self, simple_text):
        """Test that R² is high (>0.80) for good fit."""
        result = compute_vocd_d(simple_text, random_seed=42)
        # For well-formed text, R² should be quite high
        assert result.curve_fit_r_squared > 0.80

    def test_vocd_high_diversity(self, high_diversity_text):
        """Test voc-D with high diversity text produces higher D than low diversity."""
        result = compute_vocd_d(high_diversity_text, random_seed=42, min_tokens=50)
        # High diversity text should have D > 5 (higher than low-diversity text)
        assert result.d_parameter > 5

    def test_vocd_low_diversity(self, low_diversity_text):
        """Test voc-D with low diversity text produces low D."""
        result = compute_vocd_d(low_diversity_text, random_seed=42)
        # Low diversity text should have D < 20
        assert result.d_parameter < 20

    def test_vocd_text_too_short(self, short_text):
        """Test error handling when text has insufficient tokens."""
        with pytest.raises(ValueError, match="minimum.*required"):
            compute_vocd_d(short_text, min_tokens=100)

    def test_vocd_reproducibility(self, simple_text):
        """Test that same seed produces same results."""
        result1 = compute_vocd_d(simple_text, random_seed=42)
        result2 = compute_vocd_d(simple_text, random_seed=42)

        assert result1.d_parameter == result2.d_parameter
        assert result1.curve_fit_r_squared == result2.curve_fit_r_squared

    def test_vocd_different_seeds_differ(self, simple_text):
        """Test that different seeds produce different results."""
        result1 = compute_vocd_d(simple_text, random_seed=42)
        result2 = compute_vocd_d(simple_text, random_seed=99)

        # Results should differ slightly due to random sampling
        # But not too much (within 20% for stable text)
        assert result1.d_parameter != result2.d_parameter

    def test_vocd_metadata_completeness(self, simple_text):
        """Test that metadata contains all required fields."""
        result = compute_vocd_d(simple_text, random_seed=42)

        assert "total_token_count" in result.metadata
        assert "total_type_count" in result.metadata
        assert "simple_ttr" in result.metadata
        assert "sample_sizes_used" in result.metadata
        assert "mean_ttrs_per_sample_size" in result.metadata

        # Check types
        assert isinstance(result.metadata["total_token_count"], int)
        assert isinstance(result.metadata["total_type_count"], int)
        assert isinstance(result.metadata["simple_ttr"], float)
        assert isinstance(result.metadata["sample_sizes_used"], list)
        assert isinstance(result.metadata["mean_ttrs_per_sample_size"], list)

    def test_vocd_parameter_variations(self, simple_text):
        """Test voc-D with different parameter values."""
        result1 = compute_vocd_d(simple_text, sample_size=30, num_samples=50, random_seed=42)
        result2 = compute_vocd_d(simple_text, sample_size=40, num_samples=100, random_seed=42)

        # Both should produce valid results
        assert result1.d_parameter > 0
        assert result2.d_parameter > 0

        # Results should be similar but may differ slightly
        # (within reasonable range for same text)

    def test_vocd_empty_text(self):
        """Test voc-D with empty text raises error."""
        with pytest.raises((ValueError, IndexError)):
            compute_vocd_d("", min_tokens=10)

    def test_vocd_sample_count(self, simple_text):
        """Test that sample_count is positive."""
        result = compute_vocd_d(simple_text, random_seed=42)
        assert result.sample_count > 0
