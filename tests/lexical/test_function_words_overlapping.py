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
def overlapping_text():
    """Text with overlapping function words (appear in multiple categories)."""
    return "that that both both either either for for"


class TestFunctionWordsOverlapping:
    """Tests for words appearing in multiple categories."""

    def test_that_overlap(self):
        """Test 'that' counted in multiple categories.

        'that' appears in:
        - DETERMINERS
        - PRONOUNS (demonstrative)
        - Could also be in conjunctions depending on usage
        """
        text = "that that that"  # 3 occurrences
        result = compute_function_words(text)

        # "that" should be counted in both determiner and pronoun categories
        assert result.metadata["determiner_count"] >= 3
        assert result.metadata["pronoun_count"] >= 3

        # But total function word count should be 3 (counted once)
        assert result.metadata["total_function_word_count"] == 3

        # "that" should be in overlapping words
        assert "that" in result.metadata["overlapping_words"]
        assert "determiner" in result.metadata["overlapping_word_categories"]["that"]
        assert "pronoun" in result.metadata["overlapping_word_categories"]["that"]

    def test_both_overlap(self):
        """Test 'both' as determiner and conjunction."""
        text = "both both"  # 2 occurrences
        result = compute_function_words(text)

        # "both" is in both DETERMINERS and CONJUNCTIONS
        assert result.metadata["determiner_count"] >= 2
        assert result.metadata["conjunction_count"] >= 2

        # Total should count once
        assert result.metadata["total_function_word_count"] == 2

        # Should be tracked as overlapping
        assert "both" in result.metadata["overlapping_words"]

    def test_for_overlap(self):
        """Test 'for' as preposition and conjunction."""
        text = "for for for"  # 3 occurrences
        result = compute_function_words(text)

        # "for" is in both PREPOSITIONS and CONJUNCTIONS
        assert result.metadata["preposition_count"] >= 3
        assert result.metadata["conjunction_count"] >= 3

        # Total should count once
        assert result.metadata["total_function_word_count"] == 3

    def test_total_ratio_counts_once(self, overlapping_text):
        """Verify total ratio counts each token only once."""
        result = compute_function_words(overlapping_text)

        # Text: "that that both both either either for for"
        # 8 tokens, all are function words, all overlap
        assert result.metadata["total_word_count"] == 8
        assert result.metadata["total_function_word_count"] == 8
        assert result.total_function_word_ratio == 1.0  # 8/8 = 1.0

        # But category counts should sum to > 8 due to overlaps
        category_sum = (
            result.metadata["determiner_count"]
            + result.metadata["preposition_count"]
            + result.metadata["conjunction_count"]
            + result.metadata["pronoun_count"]
            + result.metadata["auxiliary_count"]
            + result.metadata["particle_count"]
        )
        assert category_sum > 8

    def test_overlapping_metadata_accuracy(self, overlapping_text):
        """Verify overlapping words tracked in metadata."""
        result = compute_function_words(overlapping_text)

        # All words in this text should be overlapping
        overlapping_words = result.metadata["overlapping_words"]
        assert "that" in overlapping_words
        assert "both" in overlapping_words
        assert "either" in overlapping_words
        assert "for" in overlapping_words

        # Each should have multiple categories listed
        for word in overlapping_words:
            categories = result.metadata["overlapping_word_categories"][word]
            assert len(categories) > 1
