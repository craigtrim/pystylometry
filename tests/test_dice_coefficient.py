"""Comprehensive tests for vocabulary overlap and similarity metrics.

This module tests the vocabulary overlap functionality, including Jaccard
similarity, Sørensen-Dice coefficient, overlap coefficient, cosine similarity,
and KL divergence.

Related GitHub Issue:
    #21 - Vocabulary Overlap and Similarity Metrics
    https://github.com/craigtrim/pystylometry/issues/21

References:
    Jaccard, P. (1912). The distribution of the flora in the alpine zone.
    Sørensen, T. (1948). A method of establishing groups of equal amplitude.
    Salton, G., & McGill, M. J. (1983). Introduction to Modern Information Retrieval.
    Kullback, S., & Leibler, R. A. (1951). On Information and Sufficiency.
    Manning, C. D., & Schütze, H. (1999). Foundations of Statistical NLP.
"""

import pytest

from pystylometry.stylistic import compute_vocabulary_overlap


class TestDiceCoefficient:
    """Test Sørensen-Dice coefficient specifically."""

    def test_dice_formula(self):
        """Verify Dice = 2|intersection| / (|A| + |B|)."""
        text1 = "a b c d"
        text2 = "c d e f"
        result = compute_vocabulary_overlap(text1, text2)

        # Vocab1 = {a, b, c, d}, Vocab2 = {c, d, e, f}
        # Intersection = {c, d} = 2
        # Dice = 2*2 / (4 + 4) = 4/8 = 0.5
        assert result.dice_coefficient == pytest.approx(0.5, rel=1e-6)

    def test_dice_vs_jaccard(self):
        """Dice coefficient is always >= Jaccard similarity."""
        text1 = "apple banana cherry date"
        text2 = "cherry date elderberry fig"
        result = compute_vocabulary_overlap(text1, text2)

        assert result.dice_coefficient >= result.jaccard_similarity
