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
def punctuation_heavy_text():
    """Text with heavy punctuation around function words."""
    return "the, (and) 'but' \"or\" -the- the! the? the; the:"


class TestFunctionWordsPunctuation:
    """Punctuation handling tests."""

    def test_trailing_punctuation(self):
        """Test function words with trailing punctuation."""
        text = "the, and. but! or?"
        result = compute_function_words(text)

        # Should strip punctuation and match
        assert "the" in result.function_word_distribution
        assert "and" in result.function_word_distribution
        assert "but" in result.function_word_distribution
        assert "or" in result.function_word_distribution

    def test_leading_punctuation(self):
        """Test function words with leading punctuation."""
        text = "'the \"and (but [or"
        result = compute_function_words(text)

        # Should strip punctuation and match
        assert "the" in result.function_word_distribution
        assert "and" in result.function_word_distribution
        assert "but" in result.function_word_distribution
        assert "or" in result.function_word_distribution

    def test_quoted_function_words(self):
        """Test function words in quotes."""
        text = "\"the\" 'and' \"but\" 'or'"
        result = compute_function_words(text)

        assert "the" in result.function_word_distribution
        assert "and" in result.function_word_distribution
        assert "but" in result.function_word_distribution
        assert "or" in result.function_word_distribution

    def test_punctuation_heavy_text(self, punctuation_heavy_text):
        """Test text with heavy punctuation around function words."""
        # Text: "the, (and) 'but' \"or\" -the- the! the? the; the:"
        result = compute_function_words(punctuation_heavy_text)

        # Should identify "the" multiple times despite punctuation
        assert "the" in result.function_word_distribution
        assert result.function_word_distribution["the"] >= 5
