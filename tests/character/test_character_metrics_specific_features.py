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
def digit_text():
    """Text with embedded numbers."""
    return "In 2024, there were 365 days. The total was 8760 hours."


@pytest.fixture
def mixed_case_text():
    """Text with varied capitalization."""
    return "NASA and FBI are acronyms. iPhone is a brand. WWW changed everything."


@pytest.fixture
def punctuation_heavy_text():
    """Text with lots of punctuation."""
    return "Wait! What? Really?! Yes... it's true: (maybe). [Or not?] {Perhaps!}"


class TestCharacterMetricsSpecificFeatures:
    """Tests for specific features and calculations."""

    def test_punctuation_variety_detection(self, punctuation_heavy_text):
        """Test punctuation variety detection."""
        result = compute_character_metrics(punctuation_heavy_text)

        # Should detect multiple punctuation types: ! ? . : ( ) [ ] { }
        assert result.punctuation_variety >= 8

        # Metadata should list unique punctuation types
        assert len(result.metadata["punctuation_types"]) >= 8

    def test_vowel_consonant_ratio(self):
        """Test vowel to consonant ratio calculation."""
        # Text with known vowel/consonant counts
        # "aaa bbb" -> 3 vowels (a), 3 consonants (b) -> ratio = 1.0
        text = "aaa bbb"
        result = compute_character_metrics(text)

        assert abs(result.vowel_consonant_ratio - 1.0) < 0.01
        assert result.metadata["vowel_count"] == 3
        assert result.metadata["consonant_count"] == 3

    def test_vowel_heavy_text(self):
        """Test vowel-heavy text."""
        text = "aaa eee iii ooo uuu"  # All vowels
        result = compute_character_metrics(text)

        # All letters are vowels, no consonants
        assert result.metadata["vowel_count"] == 15
        assert result.metadata["consonant_count"] == 0

        # Ratio should be inf or very high (vowels/0)
        assert math.isnan(result.vowel_consonant_ratio) or result.vowel_consonant_ratio == float(
            "inf"
        )

    def test_consonant_heavy_text(self):
        """Test consonant-heavy text."""
        text = "bbb ccc ddd fff ggg"  # All consonants
        result = compute_character_metrics(text)

        # All letters are consonants, no vowels
        assert result.metadata["vowel_count"] == 0
        assert result.metadata["consonant_count"] == 15

        # Ratio should be 0.0 (0 vowels / consonants)
        assert result.vowel_consonant_ratio == 0.0

    def test_digit_detection(self, digit_text):
        """Test digit detection and counting."""
        result = compute_character_metrics(digit_text)

        # Should detect all digits: 2024, 365, 8760
        # 2,0,2,4,3,6,5,8,7,6,0 = 11 digits
        assert result.digit_count == 11
        assert result.metadata["total_digits"] == 11

        # Digit ratio should be positive
        assert result.digit_ratio > 0.0

    def test_uppercase_detection(self, mixed_case_text):
        """Test uppercase letter detection."""
        result = compute_character_metrics(mixed_case_text)

        # Should detect uppercase letters: N,A,S,A,F,B,I,W,W,W
        # Plus first letters of sentences
        assert result.metadata["uppercase_count"] > 0

        # Uppercase ratio should be between 0 and 1
        assert 0.0 < result.uppercase_ratio < 1.0

    def test_all_uppercase_text(self):
        """Test text that is all uppercase."""
        text = "HELLO WORLD"
        result = compute_character_metrics(text)

        # All letters should be uppercase
        uppercase_count = result.metadata["uppercase_count"]
        total_letters = result.metadata["total_letters"]
        assert uppercase_count == total_letters

        # Uppercase ratio should be 1.0
        assert result.uppercase_ratio == 1.0

    def test_all_lowercase_text(self):
        """Test text that is all lowercase."""
        text = "hello world"
        result = compute_character_metrics(text)

        # No uppercase letters
        assert result.metadata["uppercase_count"] == 0

        # Uppercase ratio should be 0.0
        assert result.uppercase_ratio == 0.0

    def test_whitespace_detection(self):
        """Test whitespace detection."""
        text = "a  b   c    d"  # Multiple spaces
        result = compute_character_metrics(text)

        # Should count all spaces
        assert result.metadata["total_whitespace"] > 0

        # Whitespace ratio should reflect proportion of spaces
        assert result.whitespace_ratio > 0.0

    def test_sentence_segmentation(self):
        """Test sentence segmentation."""
        text = "First sentence. Second sentence! Third sentence?"
        result = compute_character_metrics(text)

        # Should detect 3 sentences
        assert result.metadata["total_sentences"] == 3

    def test_avg_sentence_length_chars(self):
        """Test average sentence length in characters."""
        # Two sentences of known length
        # "Hello." = 6 chars, "World!" = 6 chars
        text = "Hello. World!"
        result = compute_character_metrics(text)

        # Average should be 6 characters per sentence
        assert abs(result.avg_sentence_length_chars - 6.0) < 0.1
