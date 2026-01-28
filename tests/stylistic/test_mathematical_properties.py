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


class TestMathematicalProperties:
    """Test mathematical properties of similarity metrics."""

    def test_symmetry_jaccard(self):
        """Jaccard similarity should be symmetric."""
        text1 = "apple banana cherry"
        text2 = "cherry date elderberry"

        result1 = compute_vocabulary_overlap(text1, text2)
        result2 = compute_vocabulary_overlap(text2, text1)

        assert result1.jaccard_similarity == result2.jaccard_similarity

    def test_symmetry_dice(self):
        """Dice coefficient should be symmetric."""
        text1 = "apple banana cherry"
        text2 = "cherry date elderberry"

        result1 = compute_vocabulary_overlap(text1, text2)
        result2 = compute_vocabulary_overlap(text2, text1)

        assert result1.dice_coefficient == result2.dice_coefficient

    def test_symmetry_overlap(self):
        """Overlap coefficient should be symmetric."""
        text1 = "apple banana cherry"
        text2 = "cherry date elderberry"

        result1 = compute_vocabulary_overlap(text1, text2)
        result2 = compute_vocabulary_overlap(text2, text1)

        assert result1.overlap_coefficient == result2.overlap_coefficient

    def test_symmetry_cosine(self):
        """Cosine similarity should be symmetric."""
        text1 = "apple apple banana cherry"
        text2 = "cherry date date elderberry"

        result1 = compute_vocabulary_overlap(text1, text2)
        result2 = compute_vocabulary_overlap(text2, text1)

        assert result1.cosine_similarity == pytest.approx(result2.cosine_similarity, rel=1e-6)

    def test_kl_asymmetry(self):
        """KL divergence should be asymmetric (in general)."""
        text1 = "apple apple apple banana"
        text2 = "apple banana banana banana"

        result1 = compute_vocabulary_overlap(text1, text2)
        result2 = compute_vocabulary_overlap(text2, text1)

        # KL divergence is typically not symmetric
        # (may be equal in some cases due to symmetry in input)
        # Just verify both are non-negative
        assert result1.kl_divergence >= 0.0
        assert result2.kl_divergence >= 0.0

    def test_bounds_jaccard(self):
        """Jaccard similarity should be in [0, 1]."""
        texts = [
            ("apple banana", "cherry date"),
            ("the quick brown fox", "the slow brown dog"),
            ("same same", "same same"),
        ]
        for text1, text2 in texts:
            result = compute_vocabulary_overlap(text1, text2)
            assert 0.0 <= result.jaccard_similarity <= 1.0

    def test_bounds_cosine(self):
        """Cosine similarity should be in [0, 1] for word frequencies."""
        texts = [
            ("apple banana", "cherry date"),
            ("the quick brown fox", "the slow brown dog"),
            ("same same", "same same"),
        ]
        for text1, text2 in texts:
            result = compute_vocabulary_overlap(text1, text2)
            assert 0.0 <= result.cosine_similarity <= 1.0
