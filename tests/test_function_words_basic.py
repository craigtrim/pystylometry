"""Tests for function word analysis.

Related GitHub Issue:
    #13 - Function Word Analysis
    https://github.com/craigtrim/pystylometry/issues/13

Function words (determiners, prepositions, conjunctions, pronouns, auxiliary
verbs, particles) are closed-class words that authors use subconsciously and
consistently, making them powerful markers for authorship attribution.

This test suite covers:
    - Basic functionality with normal prose
    - Edge cases (empty text, no function words, only function words)
    - Constraints and invariants (ratios in [0,1], counts logical)
    - Category-specific tests (each function word type)
    - Overlapping word handling (words in multiple categories)
    - Distribution and frequency accuracy
    - Diversity metric validation
    - Case insensitivity
    - Punctuation handling
    - Real-world text samples
    - Authorship attribution scenarios

References:
    Mosteller, F., & Wallace, D. L. (1964). Inference and disputed authorship:
        The Federalist. Addison-Wesley.
    Burrows, J. (2002). 'Delta': A measure of stylistic difference and a guide
        to likely authorship. Literary and Linguistic Computing, 17(3), 267-287.
"""

import pytest

from pystylometry.lexical import compute_function_words

# ==============================================================================
# Fixtures
# ==============================================================================


# ==============================================================================
# Basic Functionality Tests
# ==============================================================================


@pytest.fixture
def sample_text():
    """Simple prose for basic testing."""
    return "The quick brown fox jumps over the lazy dog. It was a nice day."


class TestFunctionWordsBasic:
    """Basic functionality tests."""

    def test_compute_function_words_basic(self, sample_text):
        """Test basic computation with sample text."""
        result = compute_function_words(sample_text)

        # Verify all fields exist
        assert hasattr(result, "determiner_ratio")
        assert hasattr(result, "preposition_ratio")
        assert hasattr(result, "conjunction_ratio")
        assert hasattr(result, "pronoun_ratio")
        assert hasattr(result, "auxiliary_ratio")
        assert hasattr(result, "particle_ratio")
        assert hasattr(result, "total_function_word_ratio")
        assert hasattr(result, "function_word_diversity")
        assert hasattr(result, "most_frequent_function_words")
        assert hasattr(result, "least_frequent_function_words")
        assert hasattr(result, "function_word_distribution")
        assert hasattr(result, "metadata")

        # Verify ratios are reasonable (not zero for text with function words)
        assert result.total_function_word_ratio > 0.0

    def test_all_fields_exist(self, sample_text):
        """Verify all required fields are present."""
        result = compute_function_words(sample_text)

        # Check field types
        assert isinstance(result.determiner_ratio, float)
        assert isinstance(result.preposition_ratio, float)
        assert isinstance(result.conjunction_ratio, float)
        assert isinstance(result.pronoun_ratio, float)
        assert isinstance(result.auxiliary_ratio, float)
        assert isinstance(result.particle_ratio, float)
        assert isinstance(result.total_function_word_ratio, float)
        assert isinstance(result.function_word_diversity, float)
        assert isinstance(result.most_frequent_function_words, list)
        assert isinstance(result.least_frequent_function_words, list)
        assert isinstance(result.function_word_distribution, dict)
        assert isinstance(result.metadata, dict)

    def test_metadata_completeness(self, sample_text):
        """Verify metadata contains all required keys."""
        result = compute_function_words(sample_text)
        metadata = result.metadata

        # Required metadata fields
        required_keys = [
            "total_word_count",
            "total_function_word_count",
            "unique_function_word_count",
            "determiner_count",
            "preposition_count",
            "conjunction_count",
            "pronoun_count",
            "auxiliary_count",
            "particle_count",
            "determiner_list",
            "preposition_list",
            "conjunction_list",
            "pronoun_list",
            "auxiliary_list",
            "particle_list",
            "overlapping_words",
            "overlapping_word_categories",
        ]

        for key in required_keys:
            assert key in metadata, f"Missing metadata key: {key}"

    def test_distribution_non_empty(self, sample_text):
        """Verify distribution is non-empty for text with function words."""
        result = compute_function_words(sample_text)

        assert len(result.function_word_distribution) > 0
        assert isinstance(result.function_word_distribution, dict)

        # Check that all values are positive integers
        for word, count in result.function_word_distribution.items():
            assert isinstance(word, str)
            assert isinstance(count, int)
            assert count > 0

    def test_frequency_lists_format(self, sample_text):
        """Verify most/least frequent lists have correct format."""
        result = compute_function_words(sample_text)

        # Most frequent
        assert isinstance(result.most_frequent_function_words, list)
        for item in result.most_frequent_function_words:
            assert isinstance(item, tuple)
            assert len(item) == 2
            assert isinstance(item[0], str)  # word
            assert isinstance(item[1], int)  # count
            assert item[1] > 0

        # Least frequent
        assert isinstance(result.least_frequent_function_words, list)
        for item in result.least_frequent_function_words:
            assert isinstance(item, tuple)
            assert len(item) == 2
            assert isinstance(item[0], str)
            assert isinstance(item[1], int)
            assert item[1] > 0
