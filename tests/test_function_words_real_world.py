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
def academic_text():
    """Academic-style text sample."""
    return (
        "Research demonstrates that cognitive processes are influenced by "
        "various factors. However, the relationship between these variables "
        "remains unclear. Further investigation is warranted."
    )


@pytest.fixture
def fiction_text():
    """Fiction narrative sample."""
    return (
        "She walked through the forest, wondering what lay ahead. "
        "The trees whispered secrets, but she couldn't understand them. "
        "Would she ever find her way home?"
    )


@pytest.fixture
def technical_text():
    """Technical documentation sample."""
    return (
        "The function accepts a string parameter and returns a dictionary. "
        "It processes the input by tokenizing the text into words. "
        "Each word is then matched against predefined patterns."
    )


class TestFunctionWordsRealWorld:
    """Tests with realistic text samples."""

    def test_academic_text(self, academic_text):
        """Test with academic prose sample."""
        result = compute_function_words(academic_text)

        # Academic text typically has high function word ratio
        assert result.total_function_word_ratio > 0.3

        # Common academic function words should appear
        assert "that" in result.function_word_distribution
        assert "the" in result.function_word_distribution

        # Should have reasonable diversity
        assert result.function_word_diversity > 0.1

    def test_fiction_text(self, fiction_text):
        """Test with fiction narrative sample."""
        result = compute_function_words(fiction_text)

        # Fiction typically has pronouns and determiners
        assert result.pronoun_ratio > 0.0
        assert result.determiner_ratio > 0.0

        # Should have function words
        assert len(result.function_word_distribution) > 0

    def test_technical_text(self, technical_text):
        """Test with technical documentation."""
        result = compute_function_words(technical_text)

        # Technical text has function words
        assert result.total_function_word_ratio > 0.2

        # Should have articles and prepositions
        assert result.determiner_ratio > 0.0
        assert result.preposition_ratio > 0.0

    def test_informal_text(self):
        """Test with conversational text."""
        text = "Hey! How are you? I'm doing great. We should hang out sometime. What do you think?"
        result = compute_function_words(text)

        # Conversational text has many pronouns
        assert result.pronoun_ratio > 0.1

        # Should have interrogatives and auxiliaries
        assert "are" in result.function_word_distribution
        assert "do" in result.function_word_distribution

    def test_news_article(self):
        """Test with news article style."""
        text = (
            "The president announced that the new policy would take effect in the next month. "
            "Officials said the changes were necessary for the country. "
            "However, critics argue that more time is needed."
        )
        result = compute_function_words(text)

        # News has high determiner and preposition usage
        assert result.determiner_ratio > 0.1
        assert result.preposition_ratio > 0.0  # Now includes "in" and "for"

        # Common news function words
        assert "the" in result.function_word_distribution
        assert "that" in result.function_word_distribution
