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
def function_words_only():
    """Text composed entirely of function words."""
    # Changed: removed "how" as it's not in the function word lists
    return "the a an this that and but or if when where"


@pytest.fixture
def no_function_words():
    """Text with no function words."""
    return "apple banana cherry date elderberry fig grape"


class TestFunctionWordsEdgeCases:
    """Edge case handling tests."""

    def test_empty_text(self):
        """Test handling of empty string."""
        result = compute_function_words("")

        # All ratios should be 0.0
        assert result.determiner_ratio == 0.0
        assert result.preposition_ratio == 0.0
        assert result.conjunction_ratio == 0.0
        assert result.pronoun_ratio == 0.0
        assert result.auxiliary_ratio == 0.0
        assert result.particle_ratio == 0.0
        assert result.total_function_word_ratio == 0.0
        assert result.function_word_diversity == 0.0

        # Lists should be empty
        assert result.most_frequent_function_words == []
        assert result.least_frequent_function_words == []

        # Distribution should be empty
        assert result.function_word_distribution == {}

        # Metadata counts should be 0
        assert result.metadata["total_word_count"] == 0
        assert result.metadata["total_function_word_count"] == 0
        assert result.metadata["unique_function_word_count"] == 0

    def test_single_function_word(self):
        """Test text with single function word."""
        result = compute_function_words("the")

        assert result.total_function_word_ratio == 1.0  # 1/1 = 1.0
        assert result.function_word_diversity == 1.0  # 1 unique / 1 total
        assert result.determiner_ratio == 1.0  # "the" is a determiner
        assert len(result.function_word_distribution) == 1
        assert result.function_word_distribution["the"] == 1

    def test_single_non_function_word(self):
        """Test text with single non-function word."""
        result = compute_function_words("apple")

        # All ratios should be 0.0
        assert result.total_function_word_ratio == 0.0
        assert result.function_word_diversity == 0.0
        assert result.determiner_ratio == 0.0

        # Distribution should be empty
        assert result.function_word_distribution == {}

        # Total word count should be 1
        assert result.metadata["total_word_count"] == 1
        assert result.metadata["total_function_word_count"] == 0

    def test_no_function_words(self, no_function_words):
        """Test text with no function words at all."""
        result = compute_function_words(no_function_words)

        # All ratios should be 0.0
        assert result.determiner_ratio == 0.0
        assert result.preposition_ratio == 0.0
        assert result.conjunction_ratio == 0.0
        assert result.pronoun_ratio == 0.0
        assert result.auxiliary_ratio == 0.0
        assert result.particle_ratio == 0.0
        assert result.total_function_word_ratio == 0.0
        assert result.function_word_diversity == 0.0

        # Distribution and lists should be empty
        assert result.function_word_distribution == {}
        assert result.most_frequent_function_words == []
        assert result.least_frequent_function_words == []

        # But total word count should be > 0
        assert result.metadata["total_word_count"] > 0
        assert result.metadata["total_function_word_count"] == 0

    def test_only_function_words(self, function_words_only):
        """Test text composed entirely of function words."""
        result = compute_function_words(function_words_only)

        # Total ratio should be 1.0 (all words are function words)
        assert result.total_function_word_ratio == 1.0

        # Total function word count should equal total word count
        assert result.metadata["total_function_word_count"] == result.metadata["total_word_count"]

        # Distribution should contain all the words
        assert len(result.function_word_distribution) > 0

    def test_very_short_text(self):
        """Test with very short text (2-3 words)."""
        result = compute_function_words("the cat")

        assert result.metadata["total_word_count"] == 2
        assert result.determiner_ratio == 0.5  # 1/2 = 0.5
        assert "the" in result.function_word_distribution

    def test_whitespace_only(self):
        """Test text with only whitespace."""
        result = compute_function_words("   \n\t  ")

        # Should behave like empty text
        assert result.total_function_word_ratio == 0.0
        assert result.metadata["total_word_count"] == 0
