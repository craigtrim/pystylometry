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
def mixed_case_text():
    """Text with varied capitalization."""
    return "The THE the tHe I i WE we AND and"


class TestFunctionWordsCaseInsensitive:
    """Case insensitivity tests."""

    def test_uppercase_matching(self):
        """Test that 'The' matches 'the'."""
        text = "The THE the"
        result = compute_function_words(text)

        # All should be counted as "the"
        assert result.function_word_distribution["the"] == 3

    def test_mixed_case_matching(self, mixed_case_text):
        """Test mixed case text."""
        # Text: "The THE the tHe I i WE we AND and"
        result = compute_function_words(mixed_case_text)

        # Should group by lowercase
        assert result.function_word_distribution["the"] == 4
        assert result.function_word_distribution["i"] == 2
        assert result.function_word_distribution["we"] == 2
        assert result.function_word_distribution["and"] == 2

    def test_all_caps_text(self):
        """Test text in all uppercase."""
        text = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
        result = compute_function_words(text)

        # Should match lowercase function words
        assert "the" in result.function_word_distribution
        assert "over" in result.function_word_distribution
