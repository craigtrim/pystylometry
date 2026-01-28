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


class TestFunctionWordsConstraints:
    """Validation of constraints and invariants."""

    def test_ratios_in_valid_range(self, sample_text):
        """Test that all ratios are between 0 and 1."""
        result = compute_function_words(sample_text)

        assert 0.0 <= result.determiner_ratio <= 1.0
        assert 0.0 <= result.preposition_ratio <= 1.0
        assert 0.0 <= result.conjunction_ratio <= 1.0
        assert 0.0 <= result.pronoun_ratio <= 1.0
        assert 0.0 <= result.auxiliary_ratio <= 1.0
        assert 0.0 <= result.particle_ratio <= 1.0
        assert 0.0 <= result.total_function_word_ratio <= 1.0

    def test_diversity_in_valid_range(self, sample_text):
        """Test that diversity is between 0 and 1."""
        result = compute_function_words(sample_text)

        assert 0.0 <= result.function_word_diversity <= 1.0

    def test_count_constraints(self, sample_text):
        """Test that counts satisfy logical constraints."""
        result = compute_function_words(sample_text)
        metadata = result.metadata

        # Total function word count <= total word count
        assert metadata["total_function_word_count"] <= metadata["total_word_count"]

        # Unique function word count <= total function word count
        assert metadata["unique_function_word_count"] <= metadata["total_function_word_count"]

        # Sum of category counts >= total function word count (due to overlaps)
        category_sum = (
            metadata["determiner_count"]
            + metadata["preposition_count"]
            + metadata["conjunction_count"]
            + metadata["pronoun_count"]
            + metadata["auxiliary_count"]
            + metadata["particle_count"]
        )
        assert category_sum >= metadata["total_function_word_count"]

        # All counts are non-negative
        assert metadata["total_word_count"] >= 0
        assert metadata["total_function_word_count"] >= 0
        assert metadata["unique_function_word_count"] >= 0
        assert metadata["determiner_count"] >= 0
        assert metadata["preposition_count"] >= 0
        assert metadata["conjunction_count"] >= 0
        assert metadata["pronoun_count"] >= 0
        assert metadata["auxiliary_count"] >= 0
        assert metadata["particle_count"] >= 0

    def test_most_frequent_sorted_descending(self, sample_text):
        """Test that most frequent list is sorted by count descending."""
        result = compute_function_words(sample_text)

        if len(result.most_frequent_function_words) > 1:
            for i in range(len(result.most_frequent_function_words) - 1):
                current_count = result.most_frequent_function_words[i][1]
                next_count = result.most_frequent_function_words[i + 1][1]
                assert current_count >= next_count

    def test_least_frequent_sorted_ascending(self, sample_text):
        """Test that least frequent list is sorted by count ascending."""
        result = compute_function_words(sample_text)

        if len(result.least_frequent_function_words) > 1:
            for i in range(len(result.least_frequent_function_words) - 1):
                current_count = result.least_frequent_function_words[i][1]
                next_count = result.least_frequent_function_words[i + 1][1]
                assert current_count <= next_count

    def test_distribution_values_positive(self, sample_text):
        """Test that distribution values are positive integers."""
        result = compute_function_words(sample_text)

        for word, count in result.function_word_distribution.items():
            assert isinstance(count, int)
            assert count > 0

    def test_unique_count_matches_distribution_length(self, sample_text):
        """Test that unique count equals distribution length."""
        result = compute_function_words(sample_text)

        assert result.metadata["unique_function_word_count"] == len(
            result.function_word_distribution
        )
