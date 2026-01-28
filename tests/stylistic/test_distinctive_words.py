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


class TestDistinctiveWords:
    """Test distinctive word identification."""

    def test_distinctive_words_identification(self):
        """Test that distinctive words are correctly identified."""
        text1 = "apple apple banana cherry"
        text2 = "dog dog elephant frog"
        result = compute_vocabulary_overlap(text1, text2)

        # All words should be distinctive since no overlap
        text1_distinctive = [word for word, _ in result.text1_distinctive_words]
        text2_distinctive = [word for word, _ in result.text2_distinctive_words]

        assert "apple" in text1_distinctive
        assert "banana" in text1_distinctive
        assert "cherry" in text1_distinctive
        assert "dog" in text2_distinctive
        assert "elephant" in text2_distinctive
        assert "frog" in text2_distinctive

    def test_distinctive_words_scoring(self):
        """Test that distinctive words are scored by frequency."""
        text1 = "apple apple apple banana cherry"  # apple=3, banana=1, cherry=1
        text2 = "dog dog elephant"
        result = compute_vocabulary_overlap(text1, text2)

        # Apple should be the most distinctive (highest frequency)
        if result.text1_distinctive_words:
            top_word, top_score = result.text1_distinctive_words[0]
            assert top_word == "apple"
            assert top_score == 3.0
