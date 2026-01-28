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
    compute_msttr,
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


class TestMSTTR:
    """Tests for MSTTR (Mean Segmental Type-Token Ratio) metric."""

    def test_msttr_basic_functionality(self, simple_text):
        """Test basic MSTTR computation with valid text."""
        result = compute_msttr(simple_text)

        # Check all required fields exist
        assert hasattr(result, "msttr_score")
        assert hasattr(result, "segment_size")
        assert hasattr(result, "segment_count")
        assert hasattr(result, "ttr_std_dev")
        assert hasattr(result, "min_ttr")
        assert hasattr(result, "max_ttr")
        assert hasattr(result, "segment_ttrs")
        assert hasattr(result, "metadata")

        # Check types
        assert isinstance(result.msttr_score, float)
        assert isinstance(result.segment_size, int)
        assert isinstance(result.segment_count, int)
        assert isinstance(result.ttr_std_dev, float)
        assert isinstance(result.min_ttr, float)
        assert isinstance(result.max_ttr, float)
        assert isinstance(result.segment_ttrs, list)
        assert isinstance(result.metadata, dict)

    def test_msttr_score_range(self, simple_text):
        """Test that MSTTR score is between 0 and 1."""
        result = compute_msttr(simple_text)
        assert 0.0 <= result.msttr_score <= 1.0

    def test_msttr_min_max_range(self, simple_text):
        """Test that min_ttr <= msttr_score <= max_ttr."""
        result = compute_msttr(simple_text)
        assert result.min_ttr <= result.msttr_score <= result.max_ttr

    def test_msttr_segment_count(self, simple_text):
        """Test that segment_count = floor(token_count / segment_size)."""
        result = compute_msttr(simple_text, segment_size=100)
        token_count = result.metadata["total_token_count"]

        expected_segment_count = token_count // 100
        assert result.segment_count == expected_segment_count

    def test_msttr_segment_ttrs_length(self, simple_text):
        """Test that segment_ttrs has length equal to segment_count."""
        result = compute_msttr(simple_text, segment_size=100)
        assert len(result.segment_ttrs) == result.segment_count

    def test_msttr_discard_incomplete(self):
        """Test that incomplete segments are discarded."""
        # Create text with 250 tokens
        text = " ".join([f"word{i}" for i in range(250)])

        result = compute_msttr(text, segment_size=100)

        # Should have 2 complete segments (200 tokens used)
        assert result.segment_count == 2
        # Should discard 50 tokens
        assert result.metadata["tokens_discarded"] == 50
        assert result.metadata["tokens_used"] == 200

    def test_msttr_high_diversity(self, high_diversity_text):
        """Test MSTTR with high diversity text produces high score."""
        result = compute_msttr(high_diversity_text, segment_size=100)
        # High diversity text should have MSTTR > 0.60
        assert result.msttr_score > 0.60

    def test_msttr_low_diversity(self, low_diversity_text):
        """Test MSTTR with low diversity text produces low score."""
        result = compute_msttr(low_diversity_text, segment_size=100)
        # Low diversity text should have MSTTR < 0.20
        assert result.msttr_score < 0.20

    def test_msttr_text_too_short(self):
        """Test error handling when text has insufficient tokens."""
        short = "the cat sat"  # 3 tokens
        with pytest.raises(ValueError, match="minimum.*required"):
            compute_msttr(short, segment_size=100)

    def test_msttr_exact_segment_size(self):
        """Test text exactly equal to segment size."""
        # Create text with exactly 100 tokens
        text = " ".join([f"word{i}" for i in range(100)])
        result = compute_msttr(text, segment_size=100)

        # Should have exactly 1 segment
        assert result.segment_count == 1
        # std_dev should be 0 (only one segment)
        assert result.ttr_std_dev == 0.0
        # min == max == msttr_score
        assert result.min_ttr == result.max_ttr == result.msttr_score

    def test_msttr_different_segment_sizes(self, simple_text):
        """Test MSTTR with different segment sizes."""
        result1 = compute_msttr(simple_text, segment_size=50)
        result2 = compute_msttr(simple_text, segment_size=100)
        result3 = compute_msttr(simple_text, segment_size=150)

        # All should produce valid results
        assert 0.0 <= result1.msttr_score <= 1.0
        assert 0.0 <= result2.msttr_score <= 1.0
        assert 0.0 <= result3.msttr_score <= 1.0

    def test_msttr_std_dev_non_negative(self, simple_text):
        """Test that standard deviation is non-negative."""
        result = compute_msttr(simple_text)
        assert result.ttr_std_dev >= 0.0

    def test_msttr_metadata_completeness(self, simple_text):
        """Test that metadata contains all required fields."""
        result = compute_msttr(simple_text)

        assert "total_token_count" in result.metadata
        assert "total_type_count" in result.metadata
        assert "simple_ttr" in result.metadata
        assert "tokens_used" in result.metadata
        assert "tokens_discarded" in result.metadata

    def test_msttr_empty_text(self):
        """Test MSTTR with empty text raises error."""
        with pytest.raises(ValueError):
            compute_msttr("")
