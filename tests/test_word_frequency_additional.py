"""Tests for word frequency sophistication metrics.

Tests the implementation of vocabulary sophistication measurement using
corpus frequency data. Related to GitHub Issue #15.
"""

import pytest

from pystylometry.lexical import compute_word_frequency_sophistication

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


@pytest.fixture
def academic_text():
    """Academic text with sophisticated vocabulary."""
    return (
        "The research methodology employed a comprehensive approach to analyze "
        "the significant theoretical framework. The data demonstrate substantial "
        "evidence supporting the hypothesis. This analysis indicates that the "
        "results require further investigation to establish definitive conclusions. "
        "The study's primary objective involves assessing the policy implications "
        "derived from the empirical findings. Researchers must interpret these "
        "complex phenomena within the appropriate contextual parameters. "
        "The investigation utilized rigorous statistical procedures to evaluate "
        "the correlation between independent and dependent variables."
    )


@pytest.fixture
def mixed_sophistication_text():
    """Text with mixed sophistication levels."""
    return (
        "The quick brown fox jumps over the lazy dog. However, this "
        "exemplifies the utilization of both rudimentary and sophisticated "
        "lexical constructs. Basic words and complex terminology coexist "
        "within the same discourse, demonstrating heterogeneous vocabulary. "
        "The analysis requires interpretation of multifaceted linguistic patterns."
    )


class TestWordFrequencyAdditional:
    """Additional comprehensive tests."""

    def test_mixed_sophistication(self, mixed_sophistication_text):
        """Test text with mixed sophistication levels."""
        result = compute_word_frequency_sophistication(mixed_sophistication_text)

        # Should have both common and rare words
        assert result.common_word_ratio > 0.0
        assert result.rare_word_ratio > 0.0

        # Advanced ratio should be between extremes
        assert 0.1 < result.advanced_word_ratio < 0.9

    def test_metadata_fields_consistent(self, academic_text):
        """Test metadata fields are internally consistent."""
        result = compute_word_frequency_sophistication(academic_text)

        # Total words should match
        assert result.metadata["total_words"] > 0
        assert result.metadata["unique_words"] <= result.metadata["total_words"]

        # Unknown word count should match ratio
        expected_unknown_count = int(
            result.metadata["unknown_word_ratio"] * result.metadata["total_words"]
        )
        # Allow off-by-one due to rounding
        assert abs(result.metadata["unknown_words"] - expected_unknown_count) <= 1

    def test_single_sentence(self):
        """Test with a single sentence."""
        text = "The research methodology employed a comprehensive approach."
        result = compute_word_frequency_sophistication(text)

        assert result.metadata["total_words"] == 7  # 7 words in the sentence
        assert result.mean_frequency_rank > 0
        assert 0.0 <= result.academic_word_ratio <= 1.0

    def test_repeated_words(self):
        """Test with many repeated words."""
        text = "research " * 50  # Same word repeated
        result = compute_word_frequency_sophistication(text)

        assert result.metadata["total_words"] == 50
        assert result.metadata["unique_words"] == 1
        # All instances of "research" should have same frequency rank
        assert result.mean_frequency_rank == result.median_frequency_rank
