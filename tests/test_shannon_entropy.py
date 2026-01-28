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

from collections import Counter

from pystylometry.ngrams.extended_ngrams import (
    _calculate_shannon_entropy,
)

# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================


class TestShannonEntropy:
    """Tests for Shannon entropy calculation."""

    def test_uniform_distribution(self):
        """Test entropy for uniform distribution."""
        # 4 items with equal frequency = log2(4) = 2.0 bits
        counter = Counter({"a": 1, "b": 1, "c": 1, "d": 1})
        entropy = _calculate_shannon_entropy(counter)
        assert abs(entropy - 2.0) < 0.001

    def test_single_item(self):
        """Test entropy when only one item (minimum entropy)."""
        counter = Counter({"a": 10})
        entropy = _calculate_shannon_entropy(counter)
        assert entropy == 0.0

    def test_empty_counter(self):
        """Test entropy with empty counter."""
        counter = Counter()
        entropy = _calculate_shannon_entropy(counter)
        assert entropy == 0.0

    def test_skewed_distribution(self):
        """Test entropy for skewed distribution."""
        counter = Counter({"a": 10, "b": 1})
        entropy = _calculate_shannon_entropy(counter)
        # Should be between 0 and log2(2)=1
        assert 0 < entropy < 1
