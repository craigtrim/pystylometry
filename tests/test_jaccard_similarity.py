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


class TestJaccardSimilarity:
    """Test Jaccard similarity coefficient specifically."""

    def test_jaccard_formula(self):
        """Verify Jaccard = |intersection| / |union|."""
        text1 = "a b c d"
        text2 = "c d e f"
        result = compute_vocabulary_overlap(text1, text2)

        # Vocab1 = {a, b, c, d}, Vocab2 = {c, d, e, f}
        # Intersection = {c, d} = 2
        # Union = {a, b, c, d, e, f} = 6
        # Jaccard = 2/6 = 1/3
        assert result.jaccard_similarity == pytest.approx(2 / 6, rel=1e-6)

    def test_jaccard_empty_texts(self):
        """Empty texts should have Jaccard = 1.0 (both identical/empty)."""
        result = compute_vocabulary_overlap("", "")
        assert result.jaccard_similarity == 1.0
