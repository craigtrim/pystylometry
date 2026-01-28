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


class TestCosineSimilarity:
    """Test cosine similarity specifically."""

    def test_cosine_identical_frequencies(self):
        """Same word frequencies should give cosine = 1.0."""
        text1 = "word word word"
        text2 = "word word word"
        result = compute_vocabulary_overlap(text1, text2)

        assert result.cosine_similarity == pytest.approx(1.0, rel=1e-6)

    def test_cosine_proportional_frequencies(self):
        """Proportional frequencies should give cosine = 1.0."""
        text1 = "a a b b"
        text2 = "a a a a b b b b"  # Same proportions, just doubled
        result = compute_vocabulary_overlap(text1, text2)

        # Same vocabulary, proportional frequencies → cosine = 1.0
        assert result.cosine_similarity == pytest.approx(1.0, rel=1e-6)

    def test_cosine_orthogonal_texts(self):
        """No shared words should give cosine = 0.0."""
        text1 = "apple banana cherry"
        text2 = "dog elephant frog"
        result = compute_vocabulary_overlap(text1, text2)

        assert result.cosine_similarity == 0.0
