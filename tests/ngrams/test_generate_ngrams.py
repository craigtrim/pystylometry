"""Tests for extended n-gram features.

Related GitHub Issue:
    #19 - Extended N-gram Features
    https://github.com/craigtrim/pystylometry/issues/19

Tests cover:
    - Word n-grams (trigrams, 4-grams)
    - Skipgrams (n-grams with gaps)
    - Character n-grams (trigrams, 4-grams)
    - Shannon entropy calculations
    - POS n-grams (optional, requires spaCy)
"""

from pystylometry.ngrams.extended_ngrams import (
    _generate_ngrams,
)

# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================


class TestGenerateNgrams:
    """Tests for _generate_ngrams helper function."""

    def test_bigrams(self):
        """Test bigram generation."""
        sequence = ["the", "quick", "brown", "fox"]
        result = _generate_ngrams(sequence, 2)
        expected = [
            ("the", "quick"),
            ("quick", "brown"),
            ("brown", "fox"),
        ]
        assert result == expected

    def test_trigrams(self):
        """Test trigram generation."""
        sequence = ["the", "quick", "brown", "fox", "jumps"]
        result = _generate_ngrams(sequence, 3)
        expected = [
            ("the", "quick", "brown"),
            ("quick", "brown", "fox"),
            ("brown", "fox", "jumps"),
        ]
        assert result == expected

    def test_4grams(self):
        """Test 4-gram generation."""
        sequence = ["a", "b", "c", "d", "e"]
        result = _generate_ngrams(sequence, 4)
        expected = [
            ("a", "b", "c", "d"),
            ("b", "c", "d", "e"),
        ]
        assert result == expected

    def test_empty_sequence(self):
        """Test with empty sequence."""
        result = _generate_ngrams([], 3)
        assert result == []

    def test_sequence_shorter_than_n(self):
        """Test when sequence is shorter than n-gram size."""
        sequence = ["a", "b"]
        result = _generate_ngrams(sequence, 3)
        assert result == []

    def test_single_ngram(self):
        """Test when sequence length equals n-gram size."""
        sequence = ["a", "b", "c"]
        result = _generate_ngrams(sequence, 3)
        assert result == [("a", "b", "c")]
