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


class TestKLDivergence:
    """Test Kullback-Leibler divergence specifically."""

    def test_kl_identical_distributions(self):
        """Identical distributions should give KL ≈ 0."""
        text1 = "a b c d e"
        text2 = "a b c d e"
        result = compute_vocabulary_overlap(text1, text2)

        # KL divergence should be near zero for identical distributions
        assert result.kl_divergence == pytest.approx(0.0, abs=1e-6)

    def test_kl_nonnegative(self):
        """KL divergence is always non-negative."""
        text1 = "apple apple apple banana"
        text2 = "apple banana banana banana"
        result = compute_vocabulary_overlap(text1, text2)

        assert result.kl_divergence >= 0.0

    def test_kl_different_distributions(self):
        """Very different distributions should have higher KL divergence."""
        text1 = "a a a a a"  # All a's
        text2 = "b b b b b"  # All b's
        result = compute_vocabulary_overlap(text1, text2)

        # KL divergence should be high for very different distributions
        assert result.kl_divergence > 0.0
