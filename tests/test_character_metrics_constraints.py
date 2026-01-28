"""Tests for character-level metrics.

Related GitHub Issue:
    #12 - Character-Level Metrics
    https://github.com/craigtrim/pystylometry/issues/12
"""

import math

import pytest

from pystylometry.character import compute_character_metrics

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


@pytest.fixture
def sample_text():
    """Simple prose for basic testing."""
    return "The quick brown fox jumps over the lazy dog."


class TestCharacterMetricsConstraints:
    """Tests for constraints and invariants."""

    def test_ratios_between_zero_and_one(self, sample_text):
        """Test that all ratios are between 0 and 1 (or NaN)."""
        result = compute_character_metrics(sample_text)

        # Check each ratio
        ratios = [
            result.vowel_consonant_ratio,
            result.digit_ratio,
            result.uppercase_ratio,
            result.whitespace_ratio,
        ]

        for ratio in ratios:
            if not math.isnan(ratio):
                assert 0.0 <= ratio <= 1.0, f"Ratio {ratio} out of bounds"

    def test_letter_frequency_sums_to_one(self, sample_text):
        """Test that letter frequencies sum to 1.0."""
        result = compute_character_metrics(sample_text)

        total = sum(result.letter_frequency.values())
        assert abs(total - 1.0) < 0.001

    def test_counts_are_non_negative(self, sample_text):
        """Test that all counts are non-negative."""
        result = compute_character_metrics(sample_text)

        assert result.punctuation_variety >= 0
        assert result.digit_count >= 0
        assert result.metadata["total_characters"] >= 0
        assert result.metadata["total_words"] >= 0
        assert result.metadata["total_sentences"] >= 0
        assert result.metadata["total_punctuation"] >= 0
        assert result.metadata["vowel_count"] >= 0
        assert result.metadata["consonant_count"] >= 0

    def test_averages_positive_or_nan(self, sample_text):
        """Test that averages are positive or NaN."""
        result = compute_character_metrics(sample_text)

        # Word length should be positive for non-empty text
        if not math.isnan(result.avg_word_length):
            assert result.avg_word_length > 0

        # Sentence length should be positive for non-empty text
        if not math.isnan(result.avg_sentence_length_chars):
            assert result.avg_sentence_length_chars > 0

    def test_metadata_consistency(self, sample_text):
        """Test that metadata values are internally consistent."""
        result = compute_character_metrics(sample_text)

        # Total characters should equal sum of all character types
        total = (
            result.metadata["total_letters"]
            + result.metadata["total_digits"]
            + result.metadata["total_punctuation"]
            + result.metadata["total_whitespace"]
        )

        # May not be exact due to "other" characters, but should be close
        assert total <= result.metadata["total_characters"]

        # Vowels + consonants should equal total letters
        assert (
            result.metadata["vowel_count"] + result.metadata["consonant_count"]
            == result.metadata["total_letters"]
        )

        # Uppercase + lowercase should equal total letters
        assert (
            result.metadata["uppercase_count"] + result.metadata["lowercase_count"]
            == result.metadata["total_letters"]
        )
