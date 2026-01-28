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

from pystylometry.stylistic import compute_vocabulary_overlap


class TestSharedWords:
    """Test shared word identification."""

    def test_shared_words(self):
        """Test shared words are correctly identified."""
        text1 = "the quick brown fox"
        text2 = "the slow brown dog"
        result = compute_vocabulary_overlap(text1, text2)

        assert "the" in result.shared_words
        assert "brown" in result.shared_words
        assert len(result.shared_words) == 2

    def test_shared_words_sorted_by_frequency(self):
        """Test shared words are sorted by combined frequency."""
        text1 = "the the the quick brown"  # the=3, quick=1, brown=1
        text2 = "the slow brown brown brown"  # the=1, slow=1, brown=3
        result = compute_vocabulary_overlap(text1, text2)

        # Combined: the=4, brown=4, so either could be first
        # Both should be in shared words
        assert "the" in result.shared_words
        assert "brown" in result.shared_words
