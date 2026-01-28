"""Tests for word frequency sophistication metrics.

Tests the implementation of vocabulary sophistication measurement using
corpus frequency data. Related to GitHub Issue #15.
"""

import pytest

from pystylometry.lexical import compute_word_frequency_sophistication

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


@pytest.fixture
def very_common_text():
    """Text with only very common words (top 100)."""
    return (
        "The man and the woman are in the house. They have a dog and a cat. "
        "The dog is big and the cat is small. The man is good and the woman "
        "is good too. They go to the store. The store is not far from the house. "
        "It is a good day. The sun is out and it is not cold."
    ) * 2


class TestWordFrequencyEdgeCases:
    """Edge case tests."""

    def test_empty_text(self):
        """Test with empty text (should raise ValueError)."""
        with pytest.raises(ValueError, match="no valid tokens"):
            compute_word_frequency_sophistication("")

    def test_whitespace_only(self):
        """Test with whitespace-only text."""
        with pytest.raises(ValueError, match="no valid tokens"):
            compute_word_frequency_sophistication("   \n\t   ")

    def test_very_short_text(self):
        """Test with very short text (5-10 words)."""
        text = "The quick brown fox jumps"
        result = compute_word_frequency_sophistication(text)

        assert result.metadata["total_words"] == 5
        assert result.mean_frequency_rank > 0
        assert 0 <= result.rare_word_ratio <= 1.0

    def test_all_unknown_words(self):
        """Test with words not in frequency list."""
        text = "xyzzyx qwertyzz asdfghjkl zxcvbnmlk poiuytrewq " * 10
        result = compute_word_frequency_sophistication(text)

        # All words should be unknown/rare
        assert result.metadata["unknown_word_ratio"] > 0.9  # Most words unknown
        assert result.rare_word_ratio > 0.9  # Unknown words treated as rare

    def test_all_common_words(self, very_common_text):
        """Test with very common words only."""
        result = compute_word_frequency_sophistication(very_common_text)

        # Should have high common word ratio
        assert result.common_word_ratio > 0.7
        # Should have low rare word ratio
        assert result.rare_word_ratio < 0.2
        # Median rank should be low (common words have low ranks)
        # Use median instead of mean to avoid skew from unknown words
        assert result.median_frequency_rank < 500
