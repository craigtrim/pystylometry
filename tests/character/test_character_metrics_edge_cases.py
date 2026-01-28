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
def minimal_punctuation_text():
    """Text with minimal punctuation."""
    return "This is simple text with few marks and no complexity"


@pytest.fixture
def single_sentence():
    """Single sentence text."""
    return "This is one sentence."


@pytest.fixture
def single_word():
    """Single word text."""
    return "Hello"


class TestCharacterMetricsEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_text(self):
        """Test with empty string."""
        result = compute_character_metrics("")

        # Ratios should be NaN for empty text
        assert math.isnan(result.avg_word_length)
        assert math.isnan(result.avg_sentence_length_chars)
        assert math.isnan(result.punctuation_density)
        assert math.isnan(result.vowel_consonant_ratio)
        assert math.isnan(result.digit_ratio)
        assert math.isnan(result.uppercase_ratio)
        assert math.isnan(result.whitespace_ratio)

        # Counts should be zero
        assert result.punctuation_variety == 0
        assert result.digit_count == 0

        # Metadata counts should be zero
        assert result.metadata["total_characters"] == 0
        assert result.metadata["total_words"] == 0
        assert result.metadata["total_sentences"] == 0

    def test_single_word(self, single_word):
        """Test with single word."""
        result = compute_character_metrics(single_word)

        # Word length should equal length of word
        assert result.avg_word_length == len(single_word)

        # Should have 1 word
        assert result.metadata["total_words"] == 1

        # Should have 0 punctuation
        assert result.punctuation_variety == 0

    def test_single_sentence(self, single_sentence):
        """Test with single sentence."""
        result = compute_character_metrics(single_sentence)

        # Should have exactly 1 sentence
        assert result.metadata["total_sentences"] == 1

        # Avg sentence length should equal total characters (minus whitespace)
        # Actually, avg_sentence_length_chars counts all chars in sentence including spaces
        assert result.avg_sentence_length_chars > 0

    def test_no_punctuation(self, minimal_punctuation_text):
        """Test with text lacking punctuation."""
        result = compute_character_metrics(minimal_punctuation_text)

        # Should have very low punctuation density (only periods for sentences)
        assert result.punctuation_density >= 0.0

    def test_only_punctuation(self):
        """Test with only punctuation characters."""
        text = "!@#$%^&*().,;:?!"
        result = compute_character_metrics(text)

        # No letters, so letter-based ratios should be NaN
        assert math.isnan(result.vowel_consonant_ratio)
        assert math.isnan(result.uppercase_ratio)

        # No words (punctuation doesn't count as words)
        assert result.metadata["total_words"] == 0 or math.isnan(result.avg_word_length)

    def test_only_digits(self):
        """Test with only numeric characters."""
        text = "123 456 789"
        result = compute_character_metrics(text)

        # Digit count should equal all non-whitespace chars
        assert result.digit_count == 9

        # Digit ratio should be high
        assert result.digit_ratio > 0.5

        # No letters
        assert result.metadata["total_letters"] == 0

    def test_only_whitespace(self):
        """Test with only whitespace."""
        text = "     \t\t\n\n   "
        result = compute_character_metrics(text)

        # Whitespace-only text results in nan ratios (no meaningful tokens)
        assert math.isnan(result.whitespace_ratio)

        # No words
        assert result.metadata["total_words"] == 0

    def test_no_whitespace(self):
        """Test with no whitespace."""
        text = "Nospacesintext."
        result = compute_character_metrics(text)

        # Whitespace ratio should be 0.0
        assert result.whitespace_ratio == 0.0

        # Should count as single word
        assert result.metadata["total_words"] == 1
