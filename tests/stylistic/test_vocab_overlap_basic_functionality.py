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


class TestBasicFunctionality:
    """Test basic vocabulary overlap functionality."""

    def test_identical_texts(self):
        """Identical texts should have perfect similarity scores."""
        text = "The quick brown fox jumps over the lazy dog"
        result = compute_vocabulary_overlap(text, text)

        assert result.jaccard_similarity == 1.0
        assert result.dice_coefficient == 1.0
        assert result.overlap_coefficient == 1.0
        assert result.cosine_similarity == 1.0
        assert result.kl_divergence == pytest.approx(0.0, abs=1e-6)
        assert result.text1_unique_count == 0
        assert result.text2_unique_count == 0

    def test_completely_different_texts(self):
        """Completely different texts should have zero similarity."""
        text1 = "apple banana cherry"
        text2 = "dog elephant frog"
        result = compute_vocabulary_overlap(text1, text2)

        assert result.jaccard_similarity == 0.0
        assert result.dice_coefficient == 0.0
        assert result.overlap_coefficient == 0.0
        assert result.cosine_similarity == 0.0
        assert result.shared_vocab_size == 0
        assert result.text1_unique_count == 3
        assert result.text2_unique_count == 3

    def test_partial_overlap(self):
        """Test texts with partial vocabulary overlap."""
        text1 = "The quick brown fox jumps over the lazy dog"
        text2 = "The fast brown fox leaps over the sleepy dog"
        result = compute_vocabulary_overlap(text1, text2)

        # Should have some but not perfect overlap
        assert 0.0 < result.jaccard_similarity < 1.0
        assert 0.0 < result.dice_coefficient < 1.0
        assert 0.0 < result.overlap_coefficient < 1.0
        assert 0.0 < result.cosine_similarity < 1.0
        assert result.shared_vocab_size > 0
        assert result.text1_unique_count > 0
        assert result.text2_unique_count > 0
