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

from pystylometry.lexical import compute_function_words

# ==============================================================================
# Fixtures
# ==============================================================================


# ==============================================================================
# Basic Functionality Tests
# ==============================================================================


class TestFunctionWordsDiversity:
    """Diversity metric tests."""

    def test_diversity_all_unique(self):
        """Test diversity = 1.0 when all tokens unique."""
        text = "the a an this that"  # 5 unique function words, each appears once
        result = compute_function_words(text)

        # Diversity should be 1.0 (5 unique / 5 total)
        assert result.function_word_diversity == 1.0

    def test_diversity_all_same(self):
        """Test diversity with repeated single function word."""
        text = "the the the the the"  # 1 unique, 5 total
        result = compute_function_words(text)

        # Diversity should be 0.2 (1 unique / 5 total)
        assert abs(result.function_word_diversity - 0.2) < 0.01

    def test_diversity_calculation(self):
        """Verify diversity = unique / total."""
        text = "the the a a and"  # 3 unique, 5 total
        result = compute_function_words(text)

        expected_diversity = 3 / 5  # 0.6
        assert abs(result.function_word_diversity - expected_diversity) < 0.01

    def test_diversity_with_non_function_words(self):
        """Test diversity calculation with mixed content."""
        text = "the cat the dog the bird"  # 1 unique function word ("the"), 3 total
        result = compute_function_words(text)

        # 1 unique function word / 3 function word tokens
        expected_diversity = 1 / 3
        assert abs(result.function_word_diversity - expected_diversity) < 0.01
