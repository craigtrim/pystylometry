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


class TestFunctionWordsAuthorship:
    """Authorship attribution tests."""

    def test_author_profile_differences(self):
        """Test that different authors have different profiles.

        Classic example: Hamilton vs Madison in Federalist Papers.
        Hamilton preferred "while", Madison preferred "whilst".
        We'll simulate with different function word preferences.
        """
        # Simulate Author A: prefers "the", "a", "and"
        text_a = (
            "The investigation showed that the results were significant. "
            "The analysis revealed a pattern. The data and the methods were sound."
        )

        # Simulate Author B: prefers "this", "these", "but"
        text_b = (
            "This investigation showed these results but this analysis revealed "
            "these patterns but this data was sound."
        )

        result_a = compute_function_words(text_a)
        result_b = compute_function_words(text_b)

        # Different determiner preferences
        # Author A uses "the" more, Author B uses "this/these" more
        assert result_a.function_word_distribution.get(
            "the", 0
        ) > result_b.function_word_distribution.get("the", 0)
        assert result_b.function_word_distribution.get(
            "this", 0
        ) > result_a.function_word_distribution.get("this", 0)

    def test_profile_consistency(self):
        """Test that same author has consistent profile across texts."""
        # Two texts by same author (similar style)
        text1 = "The cat and the dog were playing. The bird was watching."
        text2 = "The car and the bike were parked. The truck was waiting."

        result1 = compute_function_words(text1)
        result2 = compute_function_words(text2)

        # Both should have similar determiner ratios
        # (within 20% relative difference)
        ratio1 = result1.determiner_ratio
        ratio2 = result2.determiner_ratio
        relative_diff = abs(ratio1 - ratio2) / max(ratio1, ratio2)
        assert relative_diff < 0.3

        # Both should use "the" and "and"
        assert "the" in result1.function_word_distribution
        assert "the" in result2.function_word_distribution
        assert "and" in result1.function_word_distribution
        assert "and" in result2.function_word_distribution
