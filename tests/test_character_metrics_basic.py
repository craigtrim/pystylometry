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


class TestCharacterMetricsBasic:
    """Tests for basic functionality with normal text."""

    def test_compute_character_metrics_basic(self, sample_text):
        """Test character metrics computation with sample text."""
        result = compute_character_metrics(sample_text)

        # Verify all expected attributes exist
        assert hasattr(result, "avg_word_length")
        assert hasattr(result, "avg_sentence_length_chars")
        assert hasattr(result, "punctuation_density")
        assert hasattr(result, "punctuation_variety")
        assert hasattr(result, "letter_frequency")
        assert hasattr(result, "vowel_consonant_ratio")
        assert hasattr(result, "digit_count")
        assert hasattr(result, "digit_ratio")
        assert hasattr(result, "uppercase_ratio")
        assert hasattr(result, "whitespace_ratio")
        assert hasattr(result, "metadata")

    def test_compute_character_metrics_types(self, sample_text):
        """Test that all fields have correct types."""
        result = compute_character_metrics(sample_text)

        assert isinstance(result.avg_word_length, float)
        assert isinstance(result.avg_sentence_length_chars, float)
        assert isinstance(result.punctuation_density, float)
        assert isinstance(result.punctuation_variety, float)  # Mean across chunks
        assert isinstance(result.letter_frequency, dict)
        assert isinstance(result.vowel_consonant_ratio, float)
        assert isinstance(result.digit_count, int)
        assert isinstance(result.digit_ratio, float)
        assert isinstance(result.uppercase_ratio, float)
        assert isinstance(result.whitespace_ratio, float)
        assert isinstance(result.metadata, dict)

    def test_compute_character_metrics_metadata(self, sample_text):
        """Test that metadata contains expected fields."""
        result = compute_character_metrics(sample_text)

        # Check required metadata fields
        assert "total_characters" in result.metadata
        assert "total_letters" in result.metadata
        assert "total_words" in result.metadata
        assert "total_sentences" in result.metadata
        assert "total_punctuation" in result.metadata
        assert "total_whitespace" in result.metadata
        assert "total_digits" in result.metadata
        assert "punctuation_types" in result.metadata
        assert "vowel_count" in result.metadata
        assert "consonant_count" in result.metadata
        assert "uppercase_count" in result.metadata
        assert "lowercase_count" in result.metadata

        # Verify metadata types
        assert isinstance(result.metadata["total_characters"], int)
        assert isinstance(result.metadata["total_words"], int)
        assert isinstance(result.metadata["punctuation_types"], list)

    def test_avg_word_length_calculation(self):
        """Test average word length calculation."""
        # "cat dog bird" -> 3, 3, 4 -> avg = 3.33...
        text = "cat dog bird"
        result = compute_character_metrics(text)

        expected_avg = (3 + 3 + 4) / 3
        assert abs(result.avg_word_length - expected_avg) < 0.01

    def test_punctuation_density_calculation(self):
        """Test punctuation density calculation."""
        # 5 words, 3 punctuation marks -> (3/5) * 100 = 60
        text = "Hello, world! How are you?"
        result = compute_character_metrics(text)

        # 5 words, 3 punctuation (,!?) -> 60 per 100 words
        assert abs(result.punctuation_density - 60.0) < 0.1

    def test_letter_frequency_distribution(self, sample_text):
        """Test that letter frequency is properly calculated."""
        result = compute_character_metrics(sample_text)

        # Verify it's a dict with letter keys
        assert isinstance(result.letter_frequency, dict)

        # Check all lowercase letters a-z are present
        for letter in "abcdefghijklmnopqrstuvwxyz":
            assert letter in result.letter_frequency

        # Frequencies should sum to approximately 1.0
        total_freq = sum(result.letter_frequency.values())
        assert abs(total_freq - 1.0) < 0.001

        # All frequencies should be non-negative
        for freq in result.letter_frequency.values():
            assert freq >= 0.0

    def test_letter_frequency_accuracy(self):
        """Test letter frequency accuracy with known text."""
        # Text with exactly 10 'a's and 10 letters total
        text = "aaaaaaaaaa"  # 10 a's
        result = compute_character_metrics(text)

        # 'a' should have frequency 1.0
        assert result.letter_frequency["a"] == 1.0

        # All other letters should have frequency 0.0
        for letter in "bcdefghijklmnopqrstuvwxyz":
            assert result.letter_frequency[letter] == 0.0
