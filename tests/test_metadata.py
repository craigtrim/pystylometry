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


class TestMetadata:
    """Test metadata contents."""

    def test_metadata_token_counts(self):
        """Test that metadata includes token counts."""
        text1 = "the quick brown fox"  # 4 tokens
        text2 = "the slow dog"  # 3 tokens
        result = compute_vocabulary_overlap(text1, text2)

        assert result.metadata["text1_token_count"] == 4
        assert result.metadata["text2_token_count"] == 3

    def test_metadata_frequencies(self):
        """Test that metadata includes word frequencies."""
        text1 = "the the brown"
        text2 = "the slow"
        result = compute_vocabulary_overlap(text1, text2)

        assert "text1_frequencies" in result.metadata
        assert "text2_frequencies" in result.metadata
        assert result.metadata["text1_frequencies"]["the"] == 2
        assert result.metadata["text1_frequencies"]["brown"] == 1

    def test_metadata_unique_words(self):
        """Test that metadata includes unique word lists."""
        text1 = "apple banana"
        text2 = "banana cherry"
        result = compute_vocabulary_overlap(text1, text2)

        assert "unique_to_text1" in result.metadata
        assert "unique_to_text2" in result.metadata
        assert "apple" in result.metadata["unique_to_text1"]
        assert "cherry" in result.metadata["unique_to_text2"]
