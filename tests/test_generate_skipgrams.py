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
    _generate_skipgrams,
)

# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================


class TestGenerateSkipgrams:
    """Tests for _generate_skipgrams helper function."""

    def test_2_skipgram_gap_1(self):
        """Test 2-skipgram with gap of 1 (word1 _ word3)."""
        sequence = ["the", "quick", "brown", "fox"]
        result = _generate_skipgrams(sequence, 2, 1)
        # Pattern: word at i, skip 1, word at i+2
        expected = [
            ("the", "brown"),  # positions 0, 2
            ("quick", "fox"),  # positions 1, 3
        ]
        assert result == expected

    def test_3_skipgram_gap_1(self):
        """Test 3-skipgram with gap of 1 (word1 _ word3 word4)."""
        sequence = ["a", "b", "c", "d", "e"]
        result = _generate_skipgrams(sequence, 3, 1)
        # Pattern: word at i, skip 1, then 2 contiguous words
        # Total span = 3 + 1 = 4
        expected = [
            ("a", "c", "d"),  # positions 0, 2, 3
            ("b", "d", "e"),  # positions 1, 3, 4
        ]
        assert result == expected

    def test_skipgram_sequence_too_short(self):
        """Test skipgram when sequence is too short."""
        sequence = ["a", "b"]
        result = _generate_skipgrams(sequence, 2, 1)
        assert result == []

    def test_empty_sequence(self):
        """Test skipgram with empty sequence."""
        result = _generate_skipgrams([], 2, 1)
        assert result == []
