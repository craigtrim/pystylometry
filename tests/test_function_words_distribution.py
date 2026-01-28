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


class TestFunctionWordsDistribution:
    """Distribution and frequency tests."""

    def test_most_frequent_accuracy(self):
        """Verify most frequent words are correct."""
        # Text with clear most frequent: "the" appears 5 times
        text = "the cat and the dog and the bird and the fish and the snake"
        result = compute_function_words(text)

        # "the" should be most frequent (appears 5 times)
        # "and" should be second (appears 4 times)
        most_frequent = result.most_frequent_function_words
        assert len(most_frequent) >= 2
        assert most_frequent[0][0] == "the"
        assert most_frequent[0][1] == 5
        assert most_frequent[1][0] == "and"
        assert most_frequent[1][1] == 4

    def test_least_frequent_accuracy(self):
        """Verify least frequent words are correct."""
        text = "the the the a an"  # "the" = 3, "a" = 1, "an" = 1
        result = compute_function_words(text)

        least_frequent = result.least_frequent_function_words
        # "a" and "an" should be least frequent (1 each)
        assert len(least_frequent) >= 2
        assert least_frequent[0][1] == 1
        assert least_frequent[1][1] == 1
        # Both should be either "a" or "an"
        least_words = {least_frequent[0][0], least_frequent[1][0]}
        assert "a" in least_words or "an" in least_words

    def test_distribution_completeness(self, sample_text):
        """Verify distribution contains all function words used."""
        result = compute_function_words(sample_text)

        # Every function word in most_frequent should be in distribution
        for word, count in result.most_frequent_function_words:
            assert word in result.function_word_distribution
            assert result.function_word_distribution[word] == count

        # Every function word in least_frequent should be in distribution
        for word, count in result.least_frequent_function_words:
            assert word in result.function_word_distribution
            assert result.function_word_distribution[word] == count

    def test_distribution_accuracy(self):
        """Verify distribution counts are accurate."""
        text = "the the the a a and"
        result = compute_function_words(text)

        dist = result.function_word_distribution
        assert dist["the"] == 3
        assert dist["a"] == 2
        assert dist["and"] == 1

    def test_distribution_no_zero_counts(self, sample_text):
        """Verify distribution contains no zero counts."""
        result = compute_function_words(sample_text)

        for word, count in result.function_word_distribution.items():
            assert count > 0
