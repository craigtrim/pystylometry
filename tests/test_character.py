"""Tests for character-level metrics.

Related GitHub Issue:
    #12 - Character-Level Metrics
    https://github.com/craigtrim/pystylometry/issues/12
"""

import math

import pytest

from pystylometry.character import compute_character_metrics

# ===== Fixtures =====


@pytest.fixture
def sample_text():
    """Simple prose for basic testing."""
    return "The quick brown fox jumps over the lazy dog."


@pytest.fixture
def academic_text():
    """Academic-style text sample."""
    return (
        "Research demonstrates that lexical diversity correlates with "
        "authorial sophistication. Multiple studies confirm this finding."
    )


@pytest.fixture
def mixed_case_text():
    """Text with varied capitalization."""
    return "NASA and FBI are acronyms. iPhone is a brand. WWW changed everything."


@pytest.fixture
def punctuation_heavy_text():
    """Text with lots of punctuation."""
    return "Wait! What? Really?! Yes... it's true: (maybe). [Or not?] {Perhaps!}"


@pytest.fixture
def digit_text():
    """Text with embedded numbers."""
    return "In 2024, there were 365 days. The total was 8760 hours."


@pytest.fixture
def minimal_punctuation_text():
    """Text with minimal punctuation."""
    return "This is simple text with few marks and no complexity"


@pytest.fixture
def single_word():
    """Single word text."""
    return "Hello"


@pytest.fixture
def single_sentence():
    """Single sentence text."""
    return "This is one sentence."


# ===== Basic Functionality Tests =====


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


# ===== Edge Case Tests =====


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


# ===== Constraint Tests =====


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


# ===== Specific Feature Tests =====


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


# ===== Special Character Tests =====


class TestCharacterMetricsSpecialCharacters:
    """Tests for handling special characters and formatting."""

    def test_contractions_with_apostrophes(self):
        """Test handling of contractions."""
        text = "Don't can't won't shouldn't."
        result = compute_character_metrics(text)

        # Apostrophes should be counted as punctuation
        assert result.punctuation_variety >= 2  # apostrophe and period

    def test_hyphenated_words(self):
        """Test handling of hyphenated words."""
        text = "Well-known state-of-the-art."
        result = compute_character_metrics(text)

        # Hyphens should be counted as punctuation
        assert result.punctuation_variety >= 2  # hyphen and period

    def test_multiple_sentence_delimiters(self):
        """Test text with different sentence endings."""
        text = "Question? Statement. Exclamation!"
        result = compute_character_metrics(text)

        # Should detect 3 sentences
        assert result.metadata["total_sentences"] == 3

        # Should have 3 types of punctuation
        assert result.punctuation_variety >= 3

    def test_special_punctuation(self):
        """Test special punctuation marks."""
        text = "Em-dash — or ellipsis… both work."
        result = compute_character_metrics(text)

        # Should count em-dash and ellipsis
        assert result.punctuation_variety >= 3

    def test_mixed_quotes(self):
        """Test different quote styles."""
        text = "\"Double quotes\" and 'single quotes' work."
        result = compute_character_metrics(text)

        # Should detect quote marks as punctuation
        assert result.metadata["total_punctuation"] > 0


# ===== Real-World Text Tests =====


class TestCharacterMetricsRealWorld:
    """Tests with realistic text samples."""

    def test_academic_text(self, academic_text):
        """Test with academic prose."""
        result = compute_character_metrics(academic_text)

        # Academic text typically has longer words
        assert result.avg_word_length > 4.0

        # Should have reasonable letter frequency distribution
        assert len(result.letter_frequency) == 26

        # Should have multiple sentences
        assert result.metadata["total_sentences"] >= 2

    def test_complex_real_text(self):
        """Test with complex real-world text."""
        text = (
            "In 2024, NASA's Artemis program aims to return humans to the Moon. "
            "The mission involves multiple stages: launch, orbit, descent, and return. "
            "Why? Because exploration (and science!) matters."
        )
        result = compute_character_metrics(text)

        # Verify comprehensive analysis
        assert result.avg_word_length > 0
        assert result.punctuation_variety > 5
        assert result.digit_count > 0
        assert result.uppercase_ratio > 0
        # Simple sentence segmentation splits on every .!? delimiter
        # Text has: . . ? ! . = 5 sentence delimiters
        assert result.metadata["total_sentences"] == 5

    def test_social_media_style(self):
        """Test with informal social media style text."""
        text = "OMG!!! This is AMAZING!!! Can't believe it... #wow"
        result = compute_character_metrics(text)

        # High punctuation density due to multiple exclamation marks
        assert result.punctuation_density > 20.0

        # High uppercase ratio due to OMG and AMAZING
        assert result.uppercase_ratio > 0.2

    def test_technical_documentation(self):
        """Test with technical documentation style."""
        text = (
            "Function compute_metrics(text: str) -> Result:\n"
            "    Calculate metrics for input text.\n"
            "    Returns: CharacterMetricsResult object."
        )
        result = compute_character_metrics(text)

        # Should handle code-like text
        assert result.avg_word_length > 0
        assert result.metadata["total_sentences"] >= 1

        # Should detect punctuation in code
        assert result.punctuation_variety > 3


# ===== Integration Tests =====


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
