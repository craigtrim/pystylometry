"""Tests for character-level metrics.

Related GitHub Issue:
    #12 - Character-Level Metrics
    https://github.com/craigtrim/pystylometry/issues/12
"""

import pytest

from pystylometry.character import compute_character_metrics

# ===== Fixtures =====


# ===== Basic Functionality Tests =====


@pytest.fixture
def sample_text():
    """Simple prose for basic testing."""
    return "The quick brown fox jumps over the lazy dog."


class TestCharacterMetricsIntegration:
    """Integration tests with various scenarios."""

    def test_multiple_paragraphs(self):
        """Test with multi-paragraph text."""
        text = (
            "First paragraph here. It has two sentences.\n\n"
            "Second paragraph here. It also has two sentences.\n\n"
            "Third paragraph. Final sentence."
        )
        result = compute_character_metrics(text)

        # Should count all sentences
        assert result.metadata["total_sentences"] == 6

        # Should handle newlines as whitespace
        assert result.metadata["total_whitespace"] > 0

    def test_consistency_with_repeated_analysis(self, sample_text):
        """Test that analyzing same text twice gives same results."""
        result1 = compute_character_metrics(sample_text)
        result2 = compute_character_metrics(sample_text)

        # All metrics should be identical
        assert result1.avg_word_length == result2.avg_word_length
        assert result1.punctuation_density == result2.punctuation_density
        assert result1.letter_frequency == result2.letter_frequency
        assert result1.digit_count == result2.digit_count

    def test_case_insensitive_letter_frequency(self):
        """Test that letter frequency is case-insensitive."""
        text1 = "AAA"
        text2 = "aaa"
        text3 = "AaA"

        result1 = compute_character_metrics(text1)
        result2 = compute_character_metrics(text2)
        result3 = compute_character_metrics(text3)

        # All should have identical letter frequency (all 'a')
        assert result1.letter_frequency["a"] == 1.0
        assert result2.letter_frequency["a"] == 1.0
        assert result3.letter_frequency["a"] == 1.0
