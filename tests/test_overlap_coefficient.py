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


class TestOverlapCoefficient:
    """Test overlap coefficient specifically."""

    def test_overlap_formula(self):
        """Verify Overlap = |intersection| / min(|A|, |B|)."""
        text1 = "a b c d e f"  # 6 unique words
        text2 = "d e f"  # 3 unique words
        result = compute_vocabulary_overlap(text1, text2)

        # Intersection = {d, e, f} = 3
        # min(6, 3) = 3
        # Overlap = 3/3 = 1.0
        assert result.overlap_coefficient == pytest.approx(1.0, rel=1e-6)

    def test_overlap_asymmetric_containment(self):
        """Overlap = 1.0 when smaller set is contained in larger."""
        text1 = "one two three four five six seven eight"
        text2 = "two four six"
        result = compute_vocabulary_overlap(text1, text2)

        # Text2 vocabulary is fully contained in Text1
        assert result.overlap_coefficient == 1.0
